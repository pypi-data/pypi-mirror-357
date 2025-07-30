"""
Include the services decorators to be used in
Python functions to work along with the Workflows.
"""
# Import necessary modules and libraries
import sys
import traceback
import asyncio
from warnings import warn
from functools import wraps
from typing import Any, Coroutine, Optional, Callable, Type, TypeVar, Union, get_args
from valiotlogging import log, LogLevel
# Temporal imports
from temporalio import activity as temporalio_activity
# Local imports
from .service_handler import ServiceHandler
from .base_service_plugin_mixin import BaseServicePluginMixin
from .execution_mode import ServiceExecutionMode
from .redis import get_async_client_instance, get_sync_client_instance

# ensure we have the redis client as soon as possible:
sync_redis_client = get_sync_client_instance()
async_redis_client = get_async_client_instance()

EXPECTED_ANNOTATIONS = {
    # Normal denotation
    "event": "EVENT",
    "handler": "HANDLER",
    "context": "CONTEXT",
    # Extra denotation
    "ctx": "CONTEXT",
    "evt": "EVENT",
    # Return
    "return": "RETURN",
    # The "_" annotations
    # * Context
    "_": "CONTEXT",
    "_ctx": "CONTEXT",
    "__ctx": "CONTEXT",
    "_context": "CONTEXT",
    "__context": "CONTEXT",
    # * Event
    "__": "EVENT",
    "_evt": "EVENT",
    "__evt": "EVENT",
    "_event": "EVENT",
    "__event": "EVENT",
    "init_evt": "EVENT",
}

# Define the service decorator

FuncInput = TypeVar('FuncInput')
FuncOutput = TypeVar('FuncOutput')
ServiceCallable = Union[Callable[..., Coroutine[FuncInput,
                                                FuncOutput, Any]], Callable[..., FuncOutput]]


def validate_execution_mode(name: str, execution_mode: ServiceExecutionMode, smart_service: Optional[ServiceCallable] = None) -> None:
    """Validate the execution mode of the service"""
    # Validate execution mode
    if execution_mode not in [ServiceExecutionMode.IO_BOUND, ServiceExecutionMode.CPU_BOUND]:
        raise ValueError(
            f"Invalid execution_mode: {execution_mode}. "
            f"Must be one of: {', '.join([mode.value for mode in ServiceExecutionMode])}"
        )
    # Validate CPU-bound service implementation
    if smart_service is not None and execution_mode == ServiceExecutionMode.CPU_BOUND and asyncio.iscoroutinefunction(smart_service):
        raise ValueError(
            f"CPU-bound service '{name}' must be a synchronous function, not async. "
            "CPU-bound services run in separate processes and cannot be coroutines."
        )


def get_default_task_queue(execution_mode: ServiceExecutionMode,
                           default_task_queue: Optional[str] = None) -> str:
    """Get the default task queue based on execution mode"""
    if execution_mode == ServiceExecutionMode.CPU_BOUND:
        return 'default-cpu-bound-task-queue'
    return default_task_queue or 'default-valiotworkflows-task-queue'


def static_workflow_service(
    name: str, lifecycle: str = "WORKFLOW_RUN",
    task_queue: Optional[str] = None,
    execution_mode: ServiceExecutionMode = ServiceExecutionMode.IO_BOUND,
    plugins: Optional[list[Type[BaseServicePluginMixin]]] = None,
) -> Callable:
    """
    Decorator to be used for services to be called within a "python workflow worker" context.

    This decorator has two different behaviors depending on the execution_mode:

    - With IO_BOUND mode (default): Creates a wrapper function that handles the arguments
      and provides a ServiceHandler instance automatically to the decorated function.

    - With CPU_BOUND mode: Does not create a wrapper and instead directly adds metadata
      to the decorated function. The function must accept raw arguments:
      (context, event, meta, input) and manually create its own ServiceHandler if needed.

    Args:
        name (str):
            Name of the service (must be UNIQUE, matches GraphQL's `WorkflowService.code` ).
        lifecycle (str):
            Lifecycle of the service. Default is "WORKFLOW_RUN".
        task_queue (str):
            The task queue to where this service should be run.
            Defaults to 'default-valiotworkflows-task-queue' for IO_BOUND mode
            or 'default-cpu-bound-task-queue' for CPU_BOUND mode.
        plugins (List[Type[BaseServicePluginMixin]]):
            List of plugins to be used for the service.
        execution_mode (ServiceExecutionMode):
            Mode for executing the service. Can be IO_BOUND (default, thread-based)
            or CPU_BOUND (runs in separate process).
            IMPORTANT: CPU_BOUND services must accept raw arguments (context, event, meta, input)
            and manually create ServiceHandler if needed.
    """
    if plugins is None:
        plugins = []

    # Use appropriate default task queue
    if task_queue is None:
        task_queue = get_default_task_queue(execution_mode)

    def service_decorator(smart_service: ServiceCallable) -> ServiceCallable:
        # Validate CPU-bound service implementation (module load time)
        validate_execution_mode(name, execution_mode, smart_service)

        # For CPU_BOUND mode, use a simplified approach similar to custom_service
        if execution_mode == ServiceExecutionMode.CPU_BOUND:
            # Check if the service is trying to use a handler parameter - this won't work in CPU_BOUND mode
            if hasattr(smart_service, '__annotations__') and 'handler' in smart_service.__annotations__:
                raise ValueError(
                    f"CPU-bound service '{name}' has a 'handler' parameter in its signature. "
                    "CPU-bound services cannot receive a ServiceHandler automatically.\n"
                    "Instead, create your own handler inside the function:\n"
                    "def my_service(context, event, meta, input=None):\n"
                    "    # Create handler manually\n"
                    "    handler = ServiceHandler(context, event, meta, \"WORKFLOW_RUN\", input)\n"
                    "    # Use handler as needed\n"
                    "    return result"
                )

            # 1) Remember the real module & name
            orig_mod = smart_service.__module__
            orig_name = smart_service.__name__

            # Add metadata to the original function
            smart_service.__name__ = name
            smart_service.__service_name__ = name
            smart_service.__is_service__ = True  # type: ignore
            smart_service.__service_type__ = "STATIC_WORKFLOW"  # type: ignore
            smart_service.__task_queue__ = task_queue  # type: ignore
            smart_service.__execution_mode__ = execution_mode  # type: ignore
            smart_service.__lifecycle__ = lifecycle  # type: ignore
            smart_service.__plugins__ = plugins  # type: ignore
            smart_service.__is_async__ = False  # Already validated as non-async above

            # Apply Temporal activity definition directly to the function
            decorated = temporalio_activity.defn(name=name)(smart_service)

            # Force it back into the right module & name
            decorated.__module__ = orig_mod
            decorated.__name__ = orig_name

            # Inject into the module globals for pickling support
            sys.modules[orig_mod].__dict__[orig_name] = decorated

            return smart_service

        # Below is the original IO_BOUND implementation
        # Get input type from annotations
        handler_annotation = smart_service.__annotations__.get('handler', dict)
        service_handler_args = get_args(
            handler_annotation) if handler_annotation else []
        input_type = get_args(
            handler_annotation)[0] if len(service_handler_args) > 0 else None

        # Check if service expects inputs
        expected_keys = {
            key: EXPECTED_ANNOTATIONS[key] for key in smart_service.__annotations__
            if key in EXPECTED_ANNOTATIONS and key not in ["return", "_", "__"]
        }
        expecting_inputs = False
        if len(service_handler_args) > 0:
            input_type = service_handler_args[0]
        elif any(arg not in EXPECTED_ANNOTATIONS for arg in smart_service.__annotations__):
            input_type = dict
            expecting_inputs = True
        else:
            input_type = dict

        # Helper function to finalize the wrapper with common metadata
        def finalize_wrapper(wrapper_func):
            """Apply common wrapper configurations."""
            wrapper_func.__name__ = name
            wrapper_func.__service_name__ = name  # Add service_name for reference
            wrapper_func.__is_service__ = True  # type: ignore
            wrapper_func.__service_type__ = "STATIC_WORKFLOW"  # type: ignore
            wrapper_func.__task_queue__ = task_queue  # type: ignore
            wrapper_func.__execution_mode__ = execution_mode  # type: ignore
            wrapper_func.__lifecycle__ = lifecycle  # type: ignore
            wrapper_func.__plugins__ = plugins  # type: ignore
            wrapper_func.__expecting_inputs__ = expecting_inputs  # type: ignore
            wrapper_func.__expected_keys__ = expected_keys  # type: ignore
            wrapper_func.__is_async__ = asyncio.iscoroutinefunction(
                smart_service)  # type: ignore
            wrapper_func.__wrapped__ = smart_service
            return wrapper_func

        # Create the wrapper (always async since we're only supporting IO_BOUND)
        @wraps(smart_service)
        @temporalio_activity.defn(name=name)
        async def wrapper_async(
            context: dict,
            event: dict,
            meta: dict,
            input: input_type = None  # pylint: disable=W0622 # type: ignore
        ) -> smart_service.__annotations__.get('return'):  # type: ignore
            """Wrapper function to execute before and after the actual service."""
            # * Pre-work: Initialize the ServiceHandler
            # Composing the handler type dynamically based on the plugins
            handler_type = type(
                'DynamicHandler', (ServiceHandler, *plugins), {})
            handler = handler_type(context, event, meta,
                                   lifecycle, input)
            # Map the inputs to pass them later to the service
            mapped_inputs = {
                "CONTEXT": context,
                "EVENT": event,
                "HANDLER": handler,
            }
            # ! Run pre-service hooks
            for plugin in plugins:
                if hasattr(plugin, 'pre_service'):
                    await plugin.pre_service(handler)

            # * Actual Service: Run the user-defined service
            # Get the service inputs
            service_inputs = {
                key: mapped_inputs[value]
                for key, value in expected_keys.items()
            }
            #! This is a temporary fix to support the "_" annotation
            if "_" in smart_service.__annotations__:
                # RAISE A WARNING! This should be deleted in a future release.
                warn(
                    "The '_' annotation is deprecated for the static services. " +
                    "If you're not going to use that input, please remove it. " +
                    "This could be an error in future releases.",
                    category=DeprecationWarning
                )
                service_inputs["_"] = {}
            try:
                if expecting_inputs and input is not None:
                    service_inputs.update(input)
                # Call async for IO-bound services
                return_val = await smart_service(**service_inputs)
            except Exception as e:
                # get stack trace:
                log(LogLevel.ERROR,
                    f"Error in service {name}: {traceback.format_exc()}")
                raise e

            # * Cleanup: Build the response
            response = return_val

            # ! Run post-service hooks
            for plugin in plugins:
                if hasattr(plugin, 'post_service'):
                    response = await plugin.post_service(handler, response)
            return response

        return finalize_wrapper(wrapper_async)

    return service_decorator


def workflows_studio_service(
    name: str, lifecycle: str = "WORKFLOW_RUN",
    task_queue: Optional[str] = None,
    execution_mode: ServiceExecutionMode = ServiceExecutionMode.IO_BOUND,
    plugins: Optional[list[Type[BaseServicePluginMixin]]] = None,
) -> Callable:
    """
    Decorator to be used for services to be called within an "xstateInterpreter worker" context.

    This decorator has two different behaviors depending on the execution_mode:

    - With IO_BOUND mode (default): Creates a wrapper function that handles the arguments
      and provides a ServiceHandler instance automatically to the decorated function.

    - With CPU_BOUND mode: Does not create a wrapper and instead directly adds metadata
      to the decorated function. The function must accept raw arguments:
      (context, event, meta) and manually create its own ServiceHandler if needed.

    Args:
        name (str):
            Name of the service (must be UNIQUE, matches GraphQL's `WorkflowService.code` ).
        lifecycle (str): Lifecycle of the service.
            Can be one of "WORKFLOW_RUN" or "STATE_RUN"
            Used with utilities that perform cleanup operations, like `handler.gql_subscribe`.
        task_queue (str):
            The task queue to where this service should be run.
            Defaults to 'activities-task-queue' for IO_BOUND mode
            or 'default-cpu-bound-task-queue' for CPU_BOUND mode.
        plugins (List[Type[BaseServicePluginMixin]]):
            List of plugins to be used for the service.
        execution_mode (ServiceExecutionMode):
            Mode for executing the service. Can be IO_BOUND (default, thread-based)
            or CPU_BOUND (runs in separate process).
            IMPORTANT: CPU_BOUND services must accept raw arguments (context, event, meta)
            and manually create ServiceHandler if needed.
    """
    if plugins is None:
        plugins = []

    # Use appropriate default task queue
    if task_queue is None:
        task_queue = get_default_task_queue(
            execution_mode, 'activities-task-queue')

    def service_decorator(smart_service: ServiceCallable) -> ServiceCallable:
        # Validate CPU-bound service implementation (module load time)
        validate_execution_mode(name, execution_mode, smart_service)

        # For CPU_BOUND mode, use a simplified approach similar to custom_service
        if execution_mode == ServiceExecutionMode.CPU_BOUND:
            # Check if the service is trying to use a handler parameter - this won't work in CPU_BOUND mode
            if hasattr(smart_service, '__annotations__') and 'handler' in smart_service.__annotations__:
                raise ValueError(
                    f"CPU-bound service '{name}' has a 'handler' parameter in its signature. "
                    "CPU-bound services cannot receive a ServiceHandler automatically.\n"
                    "Instead, create your own handler inside the function:\n"
                    "def my_service(context, event, meta):\n"
                    "    # Create handler manually\n"
                    "    handler = ServiceHandler(context, event, meta, \"WORKFLOW_RUN\", {})\n"
                    "    # Use handler as needed\n"
                    "    # Remember to return the correct response format for workflows_studio_service\n"
                    "    return handler.build_response(service_result)"
                )

            # 1) Remember the real module & name
            orig_mod = smart_service.__module__
            orig_name = smart_service.__name__

            # Add metadata to the original function
            smart_service.__name__ = name
            smart_service.__service_name__ = name
            smart_service.__is_service__ = True  # type: ignore
            smart_service.__service_type__ = "WORKFLOWS_STUDIO"  # type: ignore
            smart_service.__task_queue__ = task_queue  # type: ignore
            smart_service.__execution_mode__ = execution_mode  # type: ignore
            smart_service.__lifecycle__ = lifecycle  # type: ignore
            smart_service.__plugins__ = plugins  # type: ignore
            smart_service.__is_async__ = False  # Already validated as non-async above

            # Apply Temporal activity definition directly to the function
            decorated = temporalio_activity.defn(name=name)(smart_service)

            # Force it back into the right module & name
            decorated.__module__ = orig_mod
            decorated.__name__ = orig_name

            # Inject into the module globals for pickling support
            sys.modules[orig_mod].__dict__[orig_name] = decorated

            return smart_service

        # Helper function to finalize the wrapper with common metadata
        def finalize_wrapper(wrapper_func):
            """Apply common wrapper configurations."""
            wrapper_func.__name__ = name
            wrapper_func.__service_name__ = name  # Add service_name for reference
            wrapper_func.__is_service__ = True  # type: ignore
            wrapper_func.__service_type__ = "WORKFLOWS_STUDIO"  # type: ignore
            wrapper_func.__task_queue__ = task_queue  # type: ignore
            wrapper_func.__execution_mode__ = execution_mode  # type: ignore
            wrapper_func.__lifecycle__ = lifecycle  # type: ignore
            wrapper_func.__plugins__ = plugins  # type: ignore
            wrapper_func.__is_async__ = asyncio.iscoroutinefunction(
                smart_service)  # type: ignore
            wrapper_func.__wrapped__ = smart_service
            return wrapper_func

        # Create the wrapper (always async since we're only supporting IO_BOUND)
        @wraps(smart_service)
        @temporalio_activity.defn(name=name)
        async def wrapper_async(context: dict, event: dict, meta: dict):
            """Wrapper function to execute before and after the actual service."""
            # xstateInterpreter cannot pass the payload at the event level,
            # so we build it here from the metadata:
            init_event = {**event}
            if event.get('type') == 'xstate.init':
                init_event.update(meta.get('id', {}))

            # * Pre-work: Initialize the ServiceHandler
            # Composing the handler type dynamically based on the plugins
            handler_type = type(
                'DynamicHandler', (ServiceHandler, *plugins), {})
            # Create handler with empty dict as input
            handler = handler_type(
                context, init_event, meta, lifecycle, {})

            # ! Run pre-service hooks
            for plugin in plugins:
                if hasattr(plugin, 'pre_service'):
                    await plugin.pre_service(handler)

            # * Actual Service: Run the user-defined service
            try:
                return_val = await smart_service(context, init_event, handler)
            except Exception as e:
                # get stack trace:
                log(LogLevel.ERROR,
                    f"Error in service {name}: {traceback.format_exc()}")
                raise e

            # * Cleanup: Build the response
            response = handler._build_response()  # pylint: disable=W0212
            response['payload'] = return_val
            # Return also the service name
            response['_service'] = name

            # ! Run post-service hooks
            for plugin in plugins:
                if hasattr(plugin, 'post_service'):
                    response = await plugin.post_service(handler, response)

            return response

        return finalize_wrapper(wrapper_async)

    return service_decorator


def custom_service(
    name: str,
    task_queue: Optional[str] = None,
    execution_mode: Union[ServiceExecutionMode,
                          str] = ServiceExecutionMode.IO_BOUND
) -> Callable:
    '''service with any serializable arguments (not necessarily
    compatible with the standard service shape) useful for creating
    services not intended to be tracked 1-1 as part of a workflow
    state, track their progress in graphql, etc.

    Args:
        name (str):
            Name of the service.
        task_queue (str):
            The task queue to where this service should be run.
            - For IO_BOUND services, defaults to 'default-valiotworkflows-task-queue'
            - For CPU_BOUND services, defaults to 'default-cpu-bound-task-queue'
        execution_mode (ServiceExecutionMode | str):
            Execution mode for the service. Can be IO_BOUND (default, thread-based) or
            CPU_BOUND (runs in separate process).

    Examples: mutation services, like:
        - `createDatum(variable: str, value: float) -> GqlResponse )`
        - `startJob(queueName: str) -> GqlResponse`
        Or non-deterministic services, like:
        - `getExternalAPIData(url: str) -> dict`
        - `tossCoin() -> bool`
        - `rollDice() -> int`
        - `shuffleList(list: List) -> List`
    '''
    # Convert string execution_mode to enum if needed
    if isinstance(execution_mode, str):
        execution_mode = ServiceExecutionMode(execution_mode)

    # Use appropriate default task queue based on execution mode
    if task_queue is None:
        task_queue = get_default_task_queue(execution_mode)

    def service_decorator(smart_service: ServiceCallable) -> ServiceCallable:
        # Validate CPU-bound service implementation
        validate_execution_mode(name, execution_mode, smart_service)

        # 1) Remember the real module & name
        # e.g. "tests.dummy_app.services.cpu_bound_service"
        orig_mod = smart_service.__module__
        orig_name = smart_service.__name__                # e.g. "count_primes"
        # Add metadata to the original function
        smart_service.__name__ = name
        smart_service.__service_name__ = name  # Add service_name for reference
        smart_service.__is_service__ = True  # type: ignore
        smart_service.__service_type__ = "CUSTOM"  # type: ignore
        smart_service.__task_queue__ = task_queue  # type: ignore
        smart_service.__execution_mode__ = execution_mode  # type: ignore
        smart_service.__is_async__ = asyncio.iscoroutinefunction(
            smart_service)  # type: ignore

        # Apply Temporal activity definition directly to the function
        decorated = temporalio_activity.defn(name=name)(smart_service)

        # 3) Inject *that* object into the module globals
        sys.modules[orig_mod].__dict__[orig_name] = decorated

        return smart_service

    return service_decorator


# Alias the default export
service = static_workflow_service
