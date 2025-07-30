"""This module provides the `WorkflowHandler` class for running service
activities either sequentially or in parallel. It also provides the
workflow decorator to define and set workflows.
Classes:
    WorkflowHandler: A handler for managing workflow activities.
"""
import json
import os
import traceback
from typing import (
    Awaitable, Callable, Coroutine, Optional,
    Any, ParamSpec, Sequence, TypeVar, Union, Dict, TYPE_CHECKING, overload
)
import asyncio
# Extra imports
from contextlib import asynccontextmanager
from collections import deque
from datetime import UTC, timedelta, datetime
import pydash as _py
from valiotlogging import log, LogLevel

# Temporal Imports
from temporalio import workflow as temporal_workflow
from temporalio.exceptions import ActivityError, CancelledError
from valiotworkflows.service_handler_base import LogFunctionType
from valiotworkflows.utils import get_current_utc_date
from valiotworkflows.utils.compressor_mixin import CompressorMixin
# Local imports
from .events.workflow_event import WorkflowEvent
from .gql_activities import GqlActivities, extract_service_name
from .workflow_handler_base import WorkflowHandlerBase
from .workflow_handle import WorkflowHandle
from .utils import get_service_ref, merge_configs, get_token_id_from_env

T = Union[Dict[str, Any], None]  # pylint: disable=C0103
R = TypeVar('R', bound=Any)  # type: ignore
SR = TypeVar('T', bound=Any)  # type: ignore
P = ParamSpec('P')

if TYPE_CHECKING:
    from .temporal_workflow import ValiotPythonWorkflow


def get_return_annotation(func: Callable[..., T]) -> Optional[T]:
    """Get the annotation for the return type of a function."""
    if hasattr(func, "__annotations__"):
        if "return" in func.__annotations__:
            return func.__annotations__["return"]
    return None


TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "workflows-task-queue")

# ! Notas:
# caminito _meta workflow:

# 1. se emite evento desde playground
# 2. se recibe evento en workflows router
# 3. workflows router solicita a temporal.io la creación de un nuevo
#   workflow (pasando _meta en 3er argumento)
# typescript:
# 4. workflows worker (xstate) recibe solicitud de temporal y arranca el workflow con el _meta
# 5. xStateInterpreter llega a estado con invocacion de workflow hijo, y se le pasa el _meta
#   con un "parent" key añadido
# 6. xStateInterpreter llega a estado con invocacion de servicio, y se le pasa el _meta con
#   unos campos {stateRunId: serviceRunId} añadidos
# y el init.event.payload en el campo _meta.id
# 7. cuando se hace attachWorkflowRunToEvent al evento recibido por un workflow
# python:
# 4b. workflows worker (python) recibe solicitud de temporal y arranca el workflow con el _meta


class WorkflowHandler(WorkflowHandlerBase, CompressorMixin):  # pylint: disable=R0902
    """A handler for managing workflow activities.
    This class provides methods for running service activities either sequentially or in parallel.

    Attributes:
        _context (dict[str, T]): A dictionary representing the workflow context.
        _event_payload (dict[str, T]): A dictionary representing the payload of the event.
        _activities (deque[Callable[..., T]]): A deque containing activities to be executed.

    Methods:
        run_service: Run a single service with a corresponding set of arguments.
        run_parallel_services: Define a group of services in parallel, receiving
            response from both of them.
        run_custom_service: Run a single service activity with a corresponding set of arguments.
        run_static_workflow_service: Run a service activity with the workflow context, event, and metadata.
        update_workflow_context: Update the workflow context with new values.
        _ensure_state_run_created: Ensures a state run is created for the given state code.
        _flush_state_entry_intents: Ensures all pending state entries are registered before taking a material action.
        compress: Compress the given object into a compressed bytes object.
        decompress: Decompress the given compressed and encoded object into the original object.
    """
    log: LogFunctionType
    _workflow: dict[str,
                    Any]  # workflow static information (code, config, states, events, ...)
    _meta: dict[str, Any]
    _client: Any
    _task_queue: Any
    # Extra comments
    _context: dict[str, T]
    _init_event: dict[str, T]
    _last_event: dict[str, T]
    _activities: deque[Callable[..., T]]
    _current_state_codes: list[str]
    _workflow_run_id: Optional[str] = None
    _event_payload: dict[str, Any] = {}
    # Memoization cache for workflow configs
    _workflow_configs_cache: dict[str, dict] = {}
    # State tracking attributes
    _pending_state_entries: list[str] = []
    _pending_state_entry_times: dict[str, datetime] = {}
    _state_run_ids: dict[str, str] = {}
    # Timer tracking for state registration
    _state_registration_timers: dict[str, asyncio.Task] = {}
    # Default delay before auto-registering a state (in seconds)
    _DEFAULT_STATE_REGISTRATION_DELAY = 0.25  # basically a razonable debounce time

    def __init__(
        self,
            wf_instance: 'ValiotPythonWorkflow',
            wf_data: dict[str, Any],
            init_evt: dict[str, Any],
            meta: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__()
        self._workflow_instance: 'ValiotPythonWorkflow' = wf_instance
        self._workflow = wf_data
        # Initialize the context and event payload
        self._context = {}
        # TODO: refactor to use WorkflowEvent object at every init and last event usages
        self._init_event = init_evt
        self._last_event = init_evt
        # Initialize the list of activities
        self._activities = deque()
        # Add the meta values
        self._meta = meta if meta else {}
        # attach workflow temporal raw id to the workflow metadata
        self._meta = {
            **self._meta,
            "id": init_evt.get("event", {}).get("payload", {})
        }
        self._current_state_codes = []
        # Initialize state tracking attributes
        self._pending_state_entries = []
        self._pending_state_entry_times = {}
        self._state_run_ids = {}
        self._state_registration_timers = {}
        # Get the logger function
        self.log = self.__get_process_logger_function(
            workflowRunId=self._meta.get("workflowRunId", ''),
        )

    async def _prepare_service_execution(
        self,
        service: Callable[..., Awaitable],
        options: Optional[dict[str, Any]] = None
    ) -> tuple[Optional[dict], dict[str, Any]]:
        """Prepare for service execution by ensuring states are registered and creating a service run.

        This helper method ensures all pending state entries are registered, creates a service
        run if necessary, and prepares the service metadata.

        Args:
            service: The service function to execute
            options: Options for service execution

        Returns:
            tuple containing:
                - service_run: The service run information or None if no service run created
                - service_meta: The service metadata to pass to the service
        """
        # Ensure all pending state entries are registered
        await self._flush_state_entry_intents()

        # Get service reference - this is the code like "SERVICE_1"
        service_ref = get_service_ref(service)

        # Extract the service name without the workflow prefix (WORKFLOW_N.MY_SERVICE -> MY_SERVICE)
        service_name = extract_service_name(service)

        # Try to find the service ID in the workflow configuration - this is the database ID needed for GraphQL
        service_id = None
        service_config = None
        if self._workflow and "services" in self._workflow:
            # First try with the extracted service name
            service_config = _py.find(
                self._workflow["services"], lambda srv: srv["code"] == service_name)

            # If not found, try with the full service reference as fallback
            if not service_config:
                service_config = _py.find(
                    self._workflow["services"], lambda srv: srv["code"] == service_ref)

            if service_config:
                service_id = service_config.get("id")

        # If we couldn't find the service ID, log an error
        if not service_id:
            self.log(LogLevel.ERROR,
                     f"Service '{service_ref}' (extracted name: '{service_name}') not found in workflow configuration. Cannot create service run.")

        # Get the current state (most deeply nested)
        current_state_code = self._current_state_codes[-1] if self._current_state_codes else None

        # Ensure we have a state run ID if there's a current state
        current_state_run_id = None
        if current_state_code:
            # Ensure the state run is created and get its ID
            current_state_run_id = await self._ensure_state_run_created(current_state_code)
            self.log(
                LogLevel.DEBUG, f"Using state run ID for {current_state_code}: {current_state_run_id}")

        # Create a service run if we have a state run ID and service ID
        service_run = None
        if current_state_run_id and service_id:
            # Get task queue from options
            task_queue = None
            if options and 'task_queue' in options:
                task_queue = options.get('task_queue')

            # Create a service run in GraphQL
            try:
                self.log(LogLevel.DEBUG,
                         f"Creating service run with state run ID: {current_state_run_id}, service ID: {service_id}")
                service_run = await temporal_workflow.execute_local_activity_method(
                    GqlActivities.upsert_service_run,
                    args=[current_state_run_id, service_id, task_queue],
                    **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
                )
                self.log(
                    LogLevel.DEBUG, f"Created service run for {service_ref} with state {current_state_code}: {service_run}")
            except Exception as e:
                self.log(LogLevel.ERROR,
                         f"Failed to create service run: {str(e)}")
                # Continue without a service run
                service_run = None

        # Set the base service metadata
        service_meta = {
            **self._meta,
            "stateRunId": current_state_run_id,  # Set directly from our local variable
            "serviceRunId": service_run.get('id') if service_run else None,
        }

        return service_run, service_meta

    async def _finish_service_run(
        self,
        service_run: Optional[dict],
        service_meta: dict[str, Any]
    ) -> None:
        """Mark a service run as finished in GraphQL.

        Args:
            service_run: The service run information
            service_meta: The service metadata containing the serviceRunId
        """
        if service_run and service_meta.get("serviceRunId"):
            await temporal_workflow.execute_local_activity_method(
                GqlActivities.finish_service_run,
                args=[service_meta["serviceRunId"]],
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
            )

    def _get_temporal_activity_name(self, service) -> str:
        """Gets the correctly prefixed activity name for a service.

        This handles both direct service references and services registered in the workflow:
        - For registered services, adds the workflow code prefix if not already present
        - For non-registered services, maintains the original service name

        Examples:
            - For a service 'create_user' registered in workflow 'onboarding':
              Returns 'onboarding.create_user'
            - For a service already prefixed like 'onboarding.create_user':
              Returns 'onboarding.create_user' (unchanged)
            - For a non-registered service 'send_email':
              Returns 'send_email' (unchanged)

        Args:
            service (Callable or str): The service to get the activity name for

        Returns:
            str: The properly formatted service activity name
        """
        # Get the basic service reference
        service_ref = extract_service_name(service)

        # Get the current workflow code
        workflow_code = self._meta.get('workflowCode')

        # If it's already prefixed, return as is
        if workflow_code and service_ref.startswith(f"{workflow_code}."):
            return service_ref

        # Check if we need to add workflow code prefix
        if workflow_code and self._workflow and "services" in self._workflow:
            # Extract service name (simplest form without prefix)
            service_name = service_ref.split('.')[-1]

            # Check if this service exists in the workflow's service list by name
            if _py.find(self._workflow["services"], lambda srv: srv.get("code") == service_name):
                return f"{workflow_code}.{service_ref}"

        # If none of the conditions match, return the original service reference
        return service_ref

    def get_wrapped_service(
        self,
        service,
        args=None,
        options=None
    ) -> Callable[..., Coroutine]:
        """Wraps a service function to be executed as a Temporal activity.
        Args:
            service (Callable): The service function to be wrapped.
            args (list, optional): The arguments to pass to the service function. Defaults to None.
            options (dict, optional): The options to configure the
                activity execution. Defaults to None.
        Returns:
            Callable[..., dict[str, T]]: An asynchronous function that executes the
              service as a Temporal activity.
        Raises:
            ActivityError: If there is an error executing the Temporal activity.
            Exception: For any other exceptions that occur during execution.
        """
        service_args = args if args else []
        service_ref = self._get_temporal_activity_name(service)

        # Create the local async function for this service
        async def wrapped_service() -> Any:
            """Temporal Service"""
            # Get task queue from service if available
            service_task_queue = getattr(service, "__task_queue__", None)
            service_options = {}
            if service_task_queue:
                service_options["task_queue"] = service_task_queue

            # merge the default activity options with service options and user-provided options
            # priority: user options > service task queue > default options
            activity_options = merge_configs(
                GqlActivities.DEFAULT_ACTIVITY_OPTIONS,
                service_options,
                options or {}
            )
            try:
                result_type = get_return_annotation(service)
                result = await temporal_workflow.execute_activity(
                    service_ref,
                    args=service_args,
                    result_type=result_type,  # type: ignore # required for deserialization
                    **activity_options,
                )
            except ActivityError as ae:
                # Check if the underlying cause is a CancelledError
                if isinstance(ae.__cause__, CancelledError):
                    self.log(LogLevel.WARNING,
                             f"Service {service_ref} was cancelled.")
                    return None
                # Log and re-raise other errors
                self.log(LogLevel.WARNING,
                         f"Error executing Temporal Activity {service_ref}: {traceback.format_exc()}")
                raise ae
            except Exception as e:  # pylint: disable=W0718
                self.log(LogLevel.WARNING,
                         f"Exception type: {type(e).__name__}")
                self.log(LogLevel.WARNING,
                         f"Error executing Temporal Activity {service_ref}: {traceback.format_exc()}")
                raise e
            return result
        return wrapped_service

    @overload
    async def run_static_workflow_service(
        self,
        service: Union[Callable[..., Awaitable[SR]], Callable[..., SR]],
        input: Any = None,  # pylint: disable=W0622
        ignore_with: None = None,
        timeout: None = None,
        options: Optional[dict[str, Any]] = None,
    ) -> SR:
        ...

    @overload
    async def run_static_workflow_service(
        self,
        service: Union[Callable[..., Awaitable[SR]], Callable[..., SR]],
        input: Any = None,  # pylint: disable=W0622
        ignore_with: Optional[Union[str, list[str]]] = ...,
        timeout: Optional[timedelta] = ...,
        options: Optional[dict[str, Any]] = None,
    ) -> Union[SR, WorkflowEvent]:
        ...

    async def run_static_workflow_service(  # pylint: disable=R0914,R0913
        self,
        service: Union[Callable[..., Awaitable[SR]], Callable[..., SR]],
        input: Any = None,  # pylint: disable=W0622
        ignore_with: Optional[Union[str, list[str]]] = None,
        timeout: Optional[timedelta] = None,
        options: Optional[dict[str, Any]] = None
    ) -> Union[SR, WorkflowEvent]:
        """Run a single service activity (for use with services created for static
        python workflows, NOT Workflows Studio ones).
        Args:
            service (Callable[..., T]): The service activity to be executed.
            args (Optional[dict[str, T]]): Arguments for the service activity. Default to None.
        Returns:
            Union[T, WorkflowEvent]: The result of the service activity or a WorkflowEvent
                representing the early exit reason.
        """
        # Prepare for service execution
        service_run, service_meta = await self._prepare_service_execution(service, options)

        # Get the event input
        event = self.build_service_event_input()

        # Set up the service arguments
        temp_args = [self._context, event, service_meta, input]

        # wrap the service for logging, error handling, etc
        wrapped_service = self.get_wrapped_service(service, temp_args, options)

        # prepare list of events that may skip the service
        ignore_with_events = [ignore_with] if isinstance(
            ignore_with, str) else ignore_with

        # Prepare the extra racers (coroutine waiting for an event to skip the service)
        event_wait_coro = self.wait_for_any_event(ignore_with_events or [], timeout) \
            if ignore_with_events or timeout else None
        extra_racers = [event_wait_coro] if event_wait_coro else []

        # Run the service and possibly wait for an event to skip it
        # the `*extra_racers` will avoid extra racers if there are no events to wait for
        race_responses_tuple = await self.race(
            [wrapped_service(), *extra_racers],
            cancel_remaining=True
        )
        response = race_responses_tuple[0]
        event_received = race_responses_tuple[1] if extra_racers else None

        # Mark service as finished
        await self._finish_service_run(service_run, service_meta)

        # Evaluate the response
        if event_received:
            # TODO: python typings to ensure "event_received" is a WorkflowEvent by default
            exit_event: WorkflowEvent = event_received
            return exit_event  # skip the service, return the event that caused the skip
        if not response and timeout:
            # if the service didn't complete on time, return an exit event representing a timeout
            exit_event = WorkflowEvent("TIMEOUT", {})
            return exit_event
        # ! IN-CODE WORKFLOW SERVICES DON'T NEED POSTPROCESSING:
        return response

    async def run_workflow_studio_service(  # pylint: disable=R0914
        self,
        service: Union[Callable[..., Awaitable], Callable[..., Any]],
        ignore_with: Optional[Union[str, list[str]]] = None,
        timeout: Optional[timedelta] = None,
        options: Optional[dict[str, Any]] = None
    ) -> tuple[T, Optional[dict[str, T]]]:
        """Run a single service activity, to be used to invoke Workflows
        Studio services (invoked inside xstateInterpreter states).
        Args:
            service (Callable[..., T]): The service activity to be executed.
            ignore_with (Optional[Union[str, list[str]]]): The event codes that should
                    cancel the service. Default to None.
            timeout (Optional[timedelta]): The maximum time to wait for the service.
                    Default to None.
            options (Optional[dict[str, Any]]): Options for the service activity.
                    Default to None.

        Returns:
            tuple[T, Optional[dict[str, T]]]: A tuple containing the result of the service
                and the event exit payload if any.
        """
        # Get task queue from service if available
        service_task_queue = getattr(service, "__task_queue__", None)
        service_options = {}
        if service_task_queue:
            service_options["task_queue"] = service_task_queue
        # Set the default options if not provided - for workflow studio services
        # ! priority: manual task queue > service task queue > .env task queue > default task queue
        service_ref = get_service_ref(service)
        service_config = _py.find(
            self._workflow["services"], lambda srv: srv["code"] == service_ref)
        service_options = merge_configs(
            GqlActivities.DEFAULT_WFS_ACTIVITY_OPTIONS,
            service_options,
            {"task_queue": _py.get(service_config, "taskQueue.code")},
            options or {}
        )

        # Prepare for service execution
        service_run, service_meta = await self._prepare_service_execution(service, service_options)

        # Get the event input
        event = self.build_service_event_input()

        # Set up the service arguments
        temp_args = [self._context, event, service_meta]

        # Set the exit event
        exit_event = None

        # wrap the service for logging, error handling, etc
        wrapped_service = self.get_wrapped_service(
            service, temp_args, service_options)

        # prepare list of events that may skip the service
        ignore_with_events = [ignore_with] if isinstance(
            ignore_with, str) else ignore_with

        # Prepare the extra racers (coroutine waiting for an event to skip the service)
        event_wait_coro = self.wait_for_any_event(ignore_with_events or [], timeout)\
            if ignore_with_events or timeout else None
        extra_racers = [event_wait_coro] if event_wait_coro else []

        # Run the service and possibly wait for an event to skip it
        # the `*extra_racers` will avoid extra racers if there are no events to wait for
        race_responses_tuple = await self.race(
            [wrapped_service(), *extra_racers],
            cancel_remaining=True
        )
        response = race_responses_tuple[0]
        event_received = race_responses_tuple[1] if extra_racers else None

        # Mark service as finished
        await self._finish_service_run(service_run, service_meta)

        # Evaluate the response
        if event_received:
            exit_event = {
                "event": event_received.type,
                "payload": event_received.payload
            }
            return None, exit_event  # skip the service, return the event that caused the skip
        if not response and timeout:
            # if the service didn't complete on time, return an exit event representing a timeout
            exit_event = {
                "event": "TIMEOUT",
                "payload": {}
            }
            return None, exit_event

        # ! WORKFLOWS STUDIO / XSTATE WORKFLOWS POSTPROCESSING:
        # Also, evaluate if there's an update on the context
        if response["actions"]:
            if "assign" in response["actions"] and response["actions"]["assign"]:
                await self.update_workflow_context(response["actions"]["assign"]["updatedContext"])
            if "exit" in response["actions"] and response["actions"]["exit"]:
                exit_event = response["actions"]["exit"]
                self._last_event = {
                    "event": {
                        "event": {"code": exit_event["event"]},
                        "payload": exit_event["payload"]
                    }
                }
        return response["payload"], exit_event

    async def run_custom_service(
        self,
        # P are the service arguments,
        service: Callable[P, Union[Awaitable[R], R]],
        args: Optional[Sequence[Any]] = None,  # that can be passed over here
        options: Optional[dict[str, Any]] = None
    ) -> R:
        """Run a single service activity with a corresponding set of arguments.

        Args:
            service (Callable[..., T]): The custom service function
            args (Optional[dict[str, T]]): Arguments for the service. Default to None.
            options (Optional[dict[str, Any]]): Options for the service activity. Default to None.

        Returns:
            T: The result of the service activity.
        """
        service_args = args if args else []
        service_ref = self._get_temporal_activity_name(service)

        # Get task queue from service if available
        service_task_queue = getattr(service, "__task_queue__", None)
        service_options = {}
        if service_task_queue:
            service_options["task_queue"] = service_task_queue

        # merge the default activity options with service options and user-provided options
        # priority: user options > service task queue > default options
        activity_options = merge_configs(
            GqlActivities.DEFAULT_ACTIVITY_OPTIONS,
            service_options,
            options or {}
        )
        response = await temporal_workflow.execute_activity(
            service_ref,
            args=service_args,
            result_type=get_return_annotation(service),  # type: ignore
            **activity_options
        )
        return response

    # alias for run_static_workflow_service
    run_service = run_static_workflow_service

    async def run_parallel_services(
        self,
        services: list[Callable[..., T]],
        args: Optional[dict[str, T]] = None,
        options: Optional[dict[str, Any]] = None
    ):
        """Run multiple service activities in parallel.

        Args:
            services (list[Callable[..., T]]): A list of service activities to be executed.
            args (Optional[dict[str, T]]): Arguments for the service.

        Returns:
            tuple[T, list[Optional[dict[str, T]]]]: A tuple containing the combined result
                of the parallel service and a list of event exit payloads if any.
        """
        # Create the event with the args
        event = {
            "payload": self._event_payload.get("payload", None),
            "args": args
        }
        # Set the arguments passed to this function
        temp_args = [self._context, event, self._meta]
        # Initialize the events list
        events_exit = []
        # Create the local async function for this service

        async def temp_service() -> dict[str, Any]:
            """Temporal Service"""
            response: dict[str, T] = {}
            # Create default activity options with user options
            default_activity_options = merge_configs(
                GqlActivities.DEFAULT_ACTIVITY_OPTIONS,
                options or {}
            )
            try:
                # Run everything at parallel using asyncio.gather, respecting each service's task queue
                responses = await asyncio.gather(*[
                    temporal_workflow.execute_activity(
                        service,
                        temp_args,
                        **self._get_service_activity_options(service, default_activity_options)
                    )
                    for service in services
                ])
                for _r in responses:
                    if _r:
                        response[_r["_service"]] = _r
            except Exception as e:  # pylint: disable=W0718
                print("Error executing Temporal parallel Activities: ", e)
                response = {}
            # Return them as a list
            return response  # type: ignore
        responses = await temp_service()

        self._event_payload = {
            "payload": responses
        }

        # Evaluate the responses
        for _service, response in responses.items():
            if response["actions"]:  # type: ignore
                # Also, evaluate if there's an update on the context
                # type: ignore
                if "assign" in response["actions"] and response["actions"]["assign"]:
                    self._context.update(
                        response["actions"]["assign"])  # type: ignore
                # type: ignore
                if "exit" in response["actions"] and response["actions"]["exit"]:
                    exit_from_service = response["actions"]["exit"]
                    events_exit.append(
                        exit_from_service)  # type: ignore

        return self._event_payload["payload"], events_exit

    async def _get_workflow_config(self, workflow_code: str) -> dict:
        """Get workflow configuration with memoization to avoid repeated API calls.

        Args:
            workflow_code (str): The code of the workflow.

        Returns:
            dict: The workflow configuration.
        """
        if workflow_code not in self._workflow_configs_cache:
            self.log(LogLevel.DEBUG,
                     f"Fetching config for workflow {workflow_code}...")
            workflow_config = await temporal_workflow.execute_local_activity_method(
                GqlActivities.get_workflow_config,
                args=[workflow_code],
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS,
            )
            self._workflow_configs_cache[workflow_code] = workflow_config
        return self._workflow_configs_cache[workflow_code]

    async def _validate_raw_handle(self, workflow_code: str, raw_handle: dict | None = None) -> None:
        """Validate that raw_handle contains all required keys according to the workflow schema.

        Args:
            workflow_code (str): The code of the workflow.
            raw_handle (dict | None): The raw handle to validate.

        Raises:
            ValueError: If the raw_handle is missing required keys when there are required keys.
        """
        # Get the workflow config
        workflow_config = await self._get_workflow_config(workflow_code)

        # Get required keys from handleSchema or INIT event's payloadSchema
        required_keys = set()

        # First try to use handleSchema if available
        handle_schema = workflow_config.get('handleSchema', {})
        if isinstance(handle_schema, dict) and handle_schema:
            required_keys = set(handle_schema.keys())

        # If no handleSchema or it's empty, try to use INIT event's payloadSchema
        if not required_keys and workflow_config.get('events'):
            init_event = _py.find(
                workflow_config['events'],
                lambda evt: _py.get(evt, 'event.code') == 'INIT'
            )
            payload_schema = _py.get(init_event, 'payloadSchema', {})
            if isinstance(payload_schema, dict) and payload_schema:
                required_keys = set(payload_schema.keys())

        # If there are no required keys, any raw_handle (including None or {}) is valid
        if not required_keys:
            return

        # If we have required keys, then raw_handle cannot be None or empty
        if not raw_handle:
            self.log(
                LogLevel.ERROR,
                f"Raw handle for workflow {workflow_code} cannot be empty when required keys exist: {required_keys}")
            raise ValueError(
                f"Raw handle for workflow {workflow_code} cannot be empty when required keys exist: {required_keys}")

        # Validate that all required keys are present in raw_handle
        raw_handle_keys = set(raw_handle.keys())
        if not required_keys.issubset(raw_handle_keys):
            missing_keys = required_keys - raw_handle_keys
            self.log(
                LogLevel.ERROR,
                "Missing required keys in raw_handle for workflow " +
                f"{workflow_code}: {missing_keys}")
            raise ValueError(
                f"The raw_handle is missing required keys: {missing_keys}. "
                f"Required: {required_keys}, Provided: {raw_handle_keys}"
            )

    async def start_child_workflow(  # pylint: disable=R0914,R0913
        self,
        workflow: Union[Callable, str],
        raw_handle: dict,
        init_event: Optional[WorkflowEvent] = None,
        # TODO: type casting like in run_service
        input: Optional[Any] = None,  # pylint: disable=W0622, W0613
        options: Optional[dict[str, Any]] = None
    ) -> WorkflowHandle:
        """
        Start a new workflow instance.

        Args:
            workflow (Union[Callable, str]): The workflow to start.
            raw_handle (dict): The raw handle (identifier) of the workflow.
            init_event (Optional[WorkflowEvent]): The initial event of the workflow.
            input (Optional[Any]): The input of the workflow.
            options (Optional[dict[str, Any]]): Options for workflow execution.

        Returns:
            WorkflowHandle: The handle of the started workflow.
        """
        ch_wf_options = options or {}

        # Ensure all pending state entries are registered before starting a child workflow
        await self._flush_state_entry_intents()

        # Get the current state (most deeply nested)
        current_state_code = self._current_state_codes[-1] if self._current_state_codes else None

        # Ensure we have a state run ID if there's a current state
        current_state_run_id = None
        if current_state_code:
            # Ensure the state run is created and get its ID
            current_state_run_id = await self._ensure_state_run_created(current_state_code)
            self.log(
                LogLevel.DEBUG,
                f"Using parent state run ID for child workflow: {current_state_run_id}"
            )

        # ! Steps:
        # 1. Get the workflow code
        if isinstance(workflow, str):
            workflow_code = workflow
        else:
            workflow_code = getattr(
                workflow, "__workflow_name__", workflow.__name__)

        # 2. Validate the raw_handle against the workflow schema
        try:
            await self._validate_raw_handle(workflow_code, raw_handle)
        except Exception as e:
            if not isinstance(e, ValueError):
                self.log(LogLevel.WARNING,
                         f"Error validating raw_handle for workflow {workflow_code}: {str(e)}")
                # Continue with execution even if validation failed
            else:
                raise e

        # 3. Get the workflow config (using memoized method)
        workflow_config = await self._get_workflow_config(workflow_code)

        # 4. Get the workflow handle
        workflow_handle = raw_handle

        # 5. Get temporal workflow id
        self.log(LogLevel.DEBUG,
                 f"Getting temporal workflow id for {workflow_code}...")
        temporal_workflow_id = self._get_temporal_workflow_id(
            workflow_code, workflow_handle)

        # Get the task queue for this workflow
        selected_task_queue = self._get_workflow_invocation_task_queue(
            workflow, workflow_config, ch_wf_options)

        # Get token_id from environment or fallback to event's emitterTokenId
        token_id = get_token_id_from_env()
        emitter_token_id = token_id or (
            getattr(init_event, 'emitterTokenId', None) if init_event else None)

        ch_workflow_meta = {
            # minimum metadata required (ValiotPythonWorkflow picks this
            # to select the workflow to run)
            "workflowCode": workflow_code,
            "temporalWorkflowId": temporal_workflow_id,
            "emitterTokenId": emitter_token_id,
            "taskQueue": selected_task_queue,
            # Add parent state run ID for proper parent-child relationship
            "parentStateRunId": current_state_run_id,
            # Add parent metadata to create a tree of workflows
            "parent": self._meta
        }

        # 7. Prepare workflow execution arguments
        init_evt_arg = self._workflow_event_to_event_arg(
            init_event, workflow_config)
        wf_args = [workflow_config, init_evt_arg, ch_workflow_meta]
        if callable(workflow):
            result_type = get_return_annotation(workflow)
        else:
            result_type = None

        # 8. Get the taskQueue this child workflow should run on
        selected_task_queue = ch_wf_options.get('task_queue') or \
            _py.get(workflow_config, 'taskQueue.code') or TEMPORAL_TASK_QUEUE

        # 9. Get the worker type this child workflow should run on
        selected_worker_type = _py.get(workflow_config, 'config.workerType')
        workflow_type = 'ValiotPythonWorkflow' if selected_worker_type == 'STATIC_PYTHON'\
            else 'xStateInterpreter'

        # 10. Start the child workflow
        self.log(
            LogLevel.DEBUG,
            f"Invoking child workflow {workflow_code} " +
            f"with parent state run ID: {current_state_run_id}..."
        )
        ch_wf_handle = await temporal_workflow.start_child_workflow(
            workflow_type,
            args=wf_args,
            id=temporal_workflow_id,
            result_type=result_type,  # type: ignore
            task_queue=selected_task_queue,
        )

        self.log(LogLevel.DEBUG,
                 f"Handle returned from {workflow_code}, " +
                 "dont forget to await it (`await child_handle`)")

        # 11. Return the workflow handle
        return WorkflowHandle(workflow_code, raw_handle, ch_wf_handle)

    def _workflow_event_to_event_arg(
        self,
        event: Optional[WorkflowEvent],
        workflow_config: dict
    ) -> dict:
        if not event:
            return {}
        # find the event config
        workflow_event = next(
            (evt for evt in workflow_config["events"]
             if evt["event"]["code"] == event.type),
            None
        )
        init_event = next(
            (evt for evt in workflow_config["events"]
             if evt["event"]["code"] == "INIT"),
            {"payloadSchema": []}  # To avoid problems in the ID return
        )
        workflow_id = workflow_config["id"]
        if not workflow_event:
            raise ValueError(
                f"Event {event.type} not found in workflow {workflow_config['code']} events list"
            )
        event_payload = event.payload or {}
        return {
            "type": "event",
            "event": {
                "__typename": "WorkflowRunEvent",
                "workflowId": workflow_id,
                "payload": event_payload,
                "workflowRunId": None,
                "workflowRun": None,
                "emitterTokenId": event.emitterTokenId,
                "eventId": workflow_event["event"]["id"],
                # (INIT, FINISHED, CANCELLED, etc)
                "event": workflow_event["event"],
            },
            "id": {
                key: val for key, val in event_payload.items()
                if key in init_event["payloadSchema"]
            }
        }

    # ! EVENT HANDLING METHODS

    @overload
    async def get_workflow_handle(
        self,
        workflow_code: str,
        *,
        workflow_run_id: str,
        raw_handle: None = None
    ) -> Optional[WorkflowHandle]:
        ...

    @overload
    async def get_workflow_handle(
        self,
        workflow_code: str,
        *,
        workflow_run_id: None = None,
        raw_handle: dict[str, Any]
    ) -> Optional[WorkflowHandle]:
        ...

    async def get_workflow_handle(
        self,
        workflow_code: str,
        *,
        workflow_run_id: Optional[str] = None,
        raw_handle: Optional[Dict] = None
    ) -> Optional[WorkflowHandle]:
        """Get the workflow handle (utilities) for the selected workflow run.

        **Note**: Must use either the `workflow_run_id` or the `raw_handle` (not both).

        Args:
            workflow_code (str): The code of the workflow.
            workflow_run_id (Optional[str]): The ID of the workflow run. Default to None.
            raw_handle (Optional[Dict]): The raw handle of the workflow run. Default to None.

        Returns:
            str: The workflow handle.
        """
        if not workflow_run_id and not raw_handle:
            raise ValueError(
                "You must provide either the workflow_run_id or the raw_handle")
        if workflow_run_id:
            return await self._get_workflow_handle_by_wf_run_id(workflow_code, workflow_run_id)
        if raw_handle:
            return await self._get_workflow_handle_by_raw_handle(workflow_code, raw_handle)

    async def _get_workflow_handle_by_raw_handle(
        self,
        workflow_code: str,
        raw_handle: dict
    ) -> Optional[WorkflowHandle]:
        # Validate raw_handle keys against workflow schema
        try:
            await self._validate_raw_handle(workflow_code, raw_handle)
        except Exception as e:
            if not isinstance(e, ValueError):
                self.log(LogLevel.WARNING,
                         f"Error validating raw_handle for workflow {workflow_code}: {str(e)}")
                # Continue with execution even if validation failed
            else:
                raise e

        # After validation, proceed with getting the temporal workflow ID
        workflow_id = self._get_temporal_workflow_id(workflow_code, raw_handle)
        try:
            temporal_handle = temporal_workflow.get_external_workflow_handle(
                workflow_id)
            return WorkflowHandle(workflow_code, raw_handle, temporal_handle)
        except Exception as exc:
            raise ValueError(
                f"Error getting the workflow handle: {exc}") from exc
        return None

    async def _get_workflow_handle_by_wf_run_id(
        self,
        workflow_code: str,
        workflow_run_id: str
    ) -> Optional[WorkflowHandle]:
        raise NotImplementedError(
            "Method `_get_workflow_handle_by_wf_run_id` not implemented yet")

    async def wait_for_event(
        self,
        event_code: str,
        timeout: Optional[timedelta] = None
    ) -> Optional[WorkflowEvent]:
        """Wait for an event to be received at the current workflow.

        Args:
            event_code (str): The code of the event to wait for.
            timeout (Optional[timedelta]): The maximum time to wait for the event. Default to None.

        Returns:
            Optional[WorkflowEvent]: The received event if any.
        """
        # Ensure all pending state entries are registered
        await self._flush_state_entry_intents()

        _timeout = timeout.total_seconds() if timeout else None
        self.log(LogLevel.INFO, f"Waiting for event {event_code}...")
        # wait for the event
        try:
            while True:
                remaining_time = _timeout
                start_time = asyncio.get_event_loop().time()

                event: WorkflowEvent = await asyncio.wait_for(
                    self._workflow_instance._events_queue.get(),  # pylint: disable=W0212
                    timeout=remaining_time)

                if event.type == event_code:
                    self._last_event = {
                        "event": {
                            "event": {"code": event.type},
                            "payload": event.payload
                        }
                    }
                    return event

                elapsed_time = asyncio.get_event_loop().time() - start_time
                if _timeout is not None:
                    _timeout -= elapsed_time
                    if _timeout <= 0:
                        self.log(LogLevel.INFO,
                                 f"Timeout exceeded waiting for event {event_code}")
                        break
        except asyncio.TimeoutError:
            self.log(LogLevel.INFO,
                     f"Timeout exceeded waiting for event {event_code}")
            return None
        return None

    async def wait_for_any_event(
        self,
        event_codes: list[str],
        timeout: Optional[timedelta] = None
    ) -> Optional[WorkflowEvent]:
        """Wait for any event to be received at the current workflow.\n
        IMPORTANT: This method cannot be called in parallel with other event
        waiting methods, as race conditions may occur.

        Args:
            event_codes (list[str]): The codes of the events to wait for.
            timeout (Optional[timedelta]): The maximum time to wait for the event. Default to None.

        Returns:
            Optional[WorkflowEvent]: The received event if any.
        """
        # Ensure all pending state entries are registered
        await self._flush_state_entry_intents()

        _timeout = timeout.total_seconds() if timeout else None
        if event_codes:
            max_wait_str = f" for a max of {timeout}" if timeout else ""
            self.log(LogLevel.INFO,
                     f"Waiting for any event in {event_codes} {max_wait_str}...")
        # wait for the event
        try:
            while True:
                remaining_time = _timeout
                start_time = asyncio.get_event_loop().time()

                event: WorkflowEvent = await asyncio.wait_for(
                    self._workflow_instance._events_queue.get(),  # pylint: disable=W0212
                    timeout=remaining_time)

                if event.type in event_codes:
                    self._last_event = {
                        "event": {
                            "event": {"code": event.type},
                            "payload": event.payload,
                            "workflowRunEventId": event.workflowRunEventId,
                            "emitterTokenId": event.emitterTokenId
                        }
                    }
                    return event

                elapsed_time = asyncio.get_event_loop().time() - start_time
                if _timeout is not None:
                    _timeout -= elapsed_time
                    if _timeout <= 0:
                        self.log(
                            LogLevel.INFO,
                            f"Timeout exceeded waiting for any event in {event_codes}"
                        )
                        break
        except asyncio.TimeoutError:
            self.log(LogLevel.INFO,
                     f"Timeout exceeded waiting for any event in {event_codes}")
            return None
        return None

    def event_received(self, event_code: str) -> Optional[WorkflowEvent]:
        """Check if an event was received recently at the current workflow.
        Args:
            event_code (str): The code of the event to check.
        Returns:
            bool: True if the event was received, False otherwise.
        """
        evt_queue = self._workflow_instance._events_queue  # pylint: disable=W0212
        while not evt_queue.empty():
            evt: WorkflowEvent = evt_queue.get_nowait()
            if evt.type == event_code:
                self._last_event = {
                    "event": {
                        "event": {"code": evt.type},
                        "payload": evt.payload,
                        "workflowRunEventId": evt.workflowRunEventId,
                        "emitterTokenId": evt.emitterTokenId
                    }
                }
                return evt
        return None  # no matching event found

    # ! async utilities (TODO: move to a separate class?)
    async def race(self, coroutines: list[Coroutine], cancel_remaining=False) -> tuple:
        '''
        Run multiple coroutines concurrently and return the result of the first one to complete.
        Useful in the context of:
        - invoking services in parallel and waiting for the first one to complete
        - invoking a service and waiting for a timeout to occur
        - invoking a service and waiting for a specific event to occur

        Args:
            coroutines (list[Coroutine]): The list of coroutines to run concurrently.
            cancel_remaining (bool): Whether to cancel the remaining coroutines if one of them
                    completes. Default to False.
                If set to True, the remaining coroutines will be cancelled
                    and their results will be None.
                If set to False, the remaining coroutines will continue running
                    but their results will be None (ignored).
        '''
        # Create tasks from the input coroutines
        tasks = [asyncio.create_task(coroutine) for coroutine in coroutines]

        # Wait for any task to complete
        # ! must use temporal version of wait instead of asyncio.wait because
        # ! of non deterministic behavior of asyncio.wait
        # ! see https://github.com/temporalio/sdk-python/issues/429 for more details
        done, pending = await temporal_workflow.wait(  # pylint: disable=E1101 # type: ignore
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Collect results from the completed tasks in the same order as coroutines
        results = [None] * len(tasks)
        for task in done:
            index = tasks.index(task)
            results[index] = task.result()

        # Cancel the remaining tasks if requested
        if cancel_remaining and pending:
            self.log(
                LogLevel.INFO,
                "WF Handler task race finished, Cancelling remaining tasks/timers..."
            )
            for task in pending:
                task.cancel()
                try:
                    await task  # Await to allow proper task cancellation and error handling
                except asyncio.CancelledError:
                    pass  # Ignore the cancelled task exception

        # For any task that wasn't completed, its result remains None
        return tuple(results)

    # ! INTERNAL GRAPHQL REPORTING METHODS
    async def _create_workflow_run(self):
        # Extract parent workflow run ID from metadata using pydash
        parent_workflow_run_id = _py.get(self._meta, 'parent.workflowRunId')
        parent_state_run_id = _py.get(self._meta, 'parentStateRunId')

        if parent_workflow_run_id:
            self.log(
                LogLevel.DEBUG,
                f"Creating child workflow run with parent workflow: {parent_workflow_run_id}" +
                f", parent state: {parent_state_run_id}" if parent_state_run_id else ""
            )

        wf_run_task_args = [
            self._meta['workflowCode'],
            self._init_event.get('id', {}),
            self._meta.get('taskQueue'),
            parent_workflow_run_id,
            parent_state_run_id,  # New argument for parent state run ID
        ]
        # execute gql updaters as "local activities", to improve performance
        # by avoiding roundtrips to temporal and other worker
        wf_run = await temporal_workflow.execute_local_activity_method(
            GqlActivities.create_workflow_run,
            args=wf_run_task_args,
            # heartbeat only applies to non-local activities
            **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS)
        self._workflow_run_id = wf_run.get('id')
        # attach the workflow run id to the metadata for all the lifecycle of the handler:
        self._meta['workflowRunId'] = self._workflow_run_id
        # Update the log function with the new workflowRunId
        self.log = self.__get_process_logger_function(
            workflowRunId=self._workflow_run_id or 0,
        )
        return self._workflow_run_id

    async def _finish_workflow_run(self):
        # execute gql updaters as "local activities", to improve performance
        # by avoiding roundtrips to temporal and other worker
        await temporal_workflow.execute_local_activity_method(
            GqlActivities.finish_workflow_run,
            args=[self._workflow_run_id],
            # heartbeat only applies to non-local activities
            **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS)

    async def update_workflow_context(self, new_context_slice: dict):
        '''
        Update the workflow context with the new values provided in new_context_slice
        (this method will merge the new values with the existing context, not replace it)

        Args:
            new_context_slice (dict): The new values to update the context with
        '''
        self._context.update(new_context_slice)
        # then update the remote context
        # execute gql updaters as "local activities", to improve
        # performance by avoiding roundtrips to temporal and other worker
        await temporal_workflow.execute_local_activity_method(
            GqlActivities.update_workflow_context,
            args=[self._workflow_run_id, self._context or {}],
            # heartbeat only applies to non-local activities
            **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS)

    async def _schedule_state_registration(self, state_code: str) -> None:
        """Schedule automatic state registration after a safe delay.

        This ensures the state is registered in GraphQL even if no material action
        occurs for some time after entering the state.

        Args:
            state_code (str): The code of the state to register
        """
        # Cancel any existing timer for this state
        self._cancel_state_registration_timer(state_code)

        # Create a new timer task
        async def delayed_registration():
            try:
                # Wait for the delay
                await asyncio.sleep(self._DEFAULT_STATE_REGISTRATION_DELAY)
                # Check if the state is still pending registration
                if state_code in self._pending_state_entries:
                    self.log(LogLevel.DEBUG,
                             f"Auto-registering state {state_code} after debounce delay")
                    await self._ensure_state_run_created(state_code)
            except asyncio.CancelledError:
                # Timer was cancelled - this is expected behavior when a material action occurs
                pass
            except Exception as e:
                self.log(LogLevel.ERROR,
                         f"Error in delayed state registration for {state_code}: {str(e)}")
            finally:
                # Clean up the timer reference
                if state_code in self._state_registration_timers:
                    del self._state_registration_timers[state_code]

        # Start the timer task and store it
        timer_task = asyncio.create_task(delayed_registration())
        self._state_registration_timers[state_code] = timer_task

    def _cancel_state_registration_timer(self, state_code: str) -> None:
        """Cancel any pending state registration timer for the given state.

        Args:
            state_code (str): The code of the state whose timer should be cancelled
        """
        if state_code in self._state_registration_timers:
            timer = self._state_registration_timers[state_code]
            if not timer.done():
                timer.cancel()
            del self._state_registration_timers[state_code]

    @asynccontextmanager
    async def enter_state(
        self,
        state_code: str,
        # TODO: ADD FUNCIONALITY TO THE EXIT WITH PARAMETER
        exit_with: Optional[  # pylint: disable=W0613 # type: ignore
            Union[str, list[str]]
        ] = None
    ):
        """Asynchronously enters a specified state and performs necessary actions.

        This method logs the entry into the state, updates the state run using a GraphQL activity,
        and ensures that the state is properly exited even if an exception occurs.

        Args:
            state_code (str): The code representing the state to enter.
            exit_with (Optional[Union[str, list[str]]], optional): Parameter to handle exit
                functionality. Defaults to None.

        Yields:
            None: This method is a coroutine and uses `yield` to manage asynchronous context.

        Raises:
            Any exceptions that occur during the execution of the state will be handled in
            the `finally` block.
        """
        self.log(LogLevel.INFO, f"Entering state {state_code}...")

        # Track state entry
        self._current_state_codes.append(state_code)
        self._pending_state_entries.append(state_code)
        self._pending_state_entry_times[state_code] = datetime.now(UTC)

        # Schedule automatic state registration after a safe delay
        # This ensures the state is registered even if no material action occurs
        await self._schedule_state_registration(state_code)

        try:
            yield
        finally:
            # Cancel any pending timer for this state
            self._cancel_state_registration_timer(state_code)

            # Ensure the state run was created
            await self._ensure_state_run_created(state_code)

            # Get the static state ID - finish_state_run expects the static state ID, not the state run ID
            state_id = self.get_state_id(state_code)

            # Finish the state run - using workflow_run_id and static state_id (not state_run_id)
            await temporal_workflow.execute_local_activity_method(
                GqlActivities.finish_state_run,
                args=[self._workflow_run_id, state_id],
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
            )

            # Clean up tracking data
            self._current_state_codes.pop()
            if state_code in self._pending_state_entry_times:
                del self._pending_state_entry_times[state_code]

            self.log(LogLevel.INFO, f"Exiting state {state_code}")

    async def _flush_state_entry_intents(self) -> None:
        """Ensures all pending state entries are registered before taking a material action.

        This method is called before run_service, wait_for_event, or any other action
        that needs to be associated with the current state.
        """
        if not self._pending_state_entries:
            return

        self.log(
            LogLevel.DEBUG,
            f"Flushing {len(self._pending_state_entries)} pending state entries: " +
            f"{self._pending_state_entries}"
        )

        # Cancel all pending timers since we're explicitly registering now
        for state_code in list(self._pending_state_entries):
            self._cancel_state_registration_timer(state_code)

        # Process each pending state entry
        for state_code in list(self._pending_state_entries):
            # Call _ensure_state_run_created directly, it handles its own validation
            await self._ensure_state_run_created(state_code)

    # ! GENERAL METHODS
    def get_state_id(self, state_code: str):
        """
        Retrieve the state ID corresponding to the given state code.

        Args:
            state_code (str): The code of the state for which the ID is to be retrieved.

        Returns:
            str: The ID of the state corresponding to the given state code.

        Raises:
            ValueError: If the state code is not found in the workflow's states list.
        """
        # find the corresponding state_id from the state_code
        for state in self._workflow['states']:
            if state['code'] == state_code:
                return state['id']
        raise ValueError(
            f"State {state_code} not found in workflow {self._workflow['code']} states list"
        )

    def _get_temporal_workflow_id(
        self,
        workflow_code: str,
        raw_handle: Optional[dict]
    ) -> str:
        '''
        Generate a deterministic Temporal workflow ID by stitching values from raw_handle.
        The order of the keys will be sorted to ensure consistent output.
        '''
        if not raw_handle:
            return workflow_code

        sorted_keys = sorted(raw_handle.keys())
        handle_values = [str(raw_handle[k]) for k in sorted_keys]
        return f"{workflow_code}:{':'.join(handle_values)}"

    def build_service_event_input(self):
        '''Build the event argument that the service (static or
        workflows studio one) will receive as 2nd argument
        '''
        event = {
            'type': _py.get(self._last_event, "event.event.code"),
            'payload': _py.get(self._last_event, "event.payload"),
            'emitterTokenId': _py.get(self._last_event, "event.emitterTokenId"),
            'workflowRunEventId': _py.get(self._last_event, "event.workflowRunEventId")
        }
        return event

    def update_exit_event(self, event_type: str, event_data: dict):
        '''for compatibility with xStateInterpreter behaviour,
        you may call this before a call to `run_workflows_studio_service`
        to update the event the service will receive as input
        '''
        self._last_event = {
            "event": {
                "event": {"code": event_type},
                **event_data
            }
        }

    def continue_as_new(self, new_init_event_payload: Optional[dict] = None):
        '''EXPERIMENTAL: Continue the workflow as a new one, with the new_init_event_payload

        TODOs:
        - preserve context from previous workflow
        - chain workflow runs by adding run.parentRun at graphQL
        '''
        # build workflow args:
        # similar to: [wf_data_arg, wf_init_evt_arg, wf_meta_arg]
        new_init_event = {
            **self._init_event,
            "event": {
                **self._init_event["event"],  # type: ignore
                # we want basically the same event, but with the new payload
                "payload": new_init_event_payload
            }
        }
        wf_args = [self._workflow, new_init_event, self._meta]
        temporal_workflow.continue_as_new(args=wf_args)

    def __get_process_logger_function(
        self,
        workflowRunId=0,  # pylint: disable=C0103
    ):
        """Logs to STDOUT formatted to help get helpful information

        Parameters
        ----------
        workflowRunId : int, optional
            The workflow run id, by default 0
        stateRunId : int, optional
            The state run id, by default 0
        serviceRunId : int, optional
            The service run id, by default 0

        """
        # to log this in a single line, we prefer to keep it small
        task_queue = os.environ.get(
            'TEMPORAL_TASK_QUEUE', 'UNKNOWN-TASK-QUEUE')
        wf_run = str(workflowRunId).zfill(5)
        env_logging_style = os.environ.get('LOGGING_STYLE', 'JSON')
        if env_logging_style == 'DEBUG':
            def formatted_log(
                level: LogLevel,
                message: Union[str, dict],
                extra: Optional[dict] = None
            ) -> None:
                message = message if isinstance(
                    message, str) else json.dumps(message)
                date = get_current_utc_date()
                msgs = message.split('\n')
                for msg in msgs:
                    log(
                        level,
                        f'[D={date}/WfR={wf_run}] - {msg}',
                        extra=extra
                    )
        else:
            # as we log this in JSON format, it can be human-readable
            workflow_code = self._meta.get('workflowCode')

            def formatted_log(
                level: LogLevel,
                message: Union[str, dict],
                extra: Optional[dict] = None
            ) -> None:
                message = message if isinstance(
                    message, str) else json.dumps(message)
                extra_params = extra if extra else {}
                date = get_current_utc_date()
                log(level, message, extra={
                    'date': date,
                    'taskQueue': task_queue,
                    'workflowRunId': wf_run,
                    'workflow': workflow_code,
                    **self._meta,
                    **extra_params
                })
        return formatted_log

    def _get_workflow_invocation_task_queue(
        self,
        workflow: Union[Callable, str],
        workflow_config: dict,
        options: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        """Determine the appropriate task queue for a workflow.

        Priority:
        1. Explicitly provided in options
        2. From workflow_config (GraphQL)
        3. From workflow definition

        Args:
            workflow: The workflow function or code
            workflow_config: The workflow configuration from GraphQL
            options: Options that may contain a task_queue override

        Returns:
            Optional[str]: The determined task queue or None if not found
        """
        # 1. Check options first
        if options and options.get('task_queue'):
            return options.get('task_queue')

        # 2. Check workflow_config from GraphQL
        config_task_queue = _py.get(workflow_config, 'taskQueue.code')
        if config_task_queue:
            return config_task_queue

        # 3. Check workflow definition
        if callable(workflow):
            # Check if workflow function has a task queue defined directly on it
            wf_task_queue = getattr(workflow, '__task_queue__', None)
            if wf_task_queue:
                return wf_task_queue

            # If workflow has a definition with task_queue attribute
            if hasattr(workflow, '__vw_defn__'):
                wf_defn_task_queue = getattr(
                    workflow.__vw_defn__, 'task_queue', None)
                if wf_defn_task_queue:
                    return wf_defn_task_queue

        # If no task queue found, log warning and return None
        workflow_code = workflow if isinstance(
            workflow, str) else getattr(workflow, "__workflow_name__", workflow.__name__)
        self.log(LogLevel.WARNING,
                 f"No task queue specified for workflow {workflow_code}. " +
                 "This may cause routing issues.")
        return None

    async def _ensure_state_run_created(self, state_code: str) -> str:
        """Ensures a state run is created for the given state code.

        If the state has already been registered, returns the existing state run ID.
        Otherwise, creates a new state run in GraphQL and returns the new state run ID.

        Args:
            state_code (str): The code of the state to register

        Returns:
            str: The state run ID for the given state code
        """
        # If we already have a state run ID for this state, return it
        if state_code in self._state_run_ids:
            return self._state_run_ids[state_code]

        # Get the static state ID
        state_id = self.get_state_id(state_code)

        # Call upsert_state_run GraphQL activity
        # Note: upsert_state_run internally uses datetime.now() for enteredAt
        act_args = [self._workflow_run_id, state_id]
        self.log(LogLevel.DEBUG,
                 f"Upserting state run for {state_code} with ID {state_id}")
        state_run = await temporal_workflow.execute_local_activity_method(
            GqlActivities.upsert_state_run,
            args=act_args,
            **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
        )

        # Store the resulting dynamic state run ID
        state_run_id = state_run.get('id', 0)
        self._state_run_ids[state_code] = state_run_id

        # Remove from pending state entries
        if state_code in self._pending_state_entries:
            self._pending_state_entries.remove(state_code)

        self.log(LogLevel.DEBUG,
                 f"Registered state run for {state_code}: {state_run_id}")
        return state_run_id

    async def _update_workflow_last_run_at(self) -> None:
        """Updates the lastRunAt timestamp of the workflow in GraphQL.

        Uses the GqlActivities.update_workflow_last_run_at activity to update
        the lastRunAt field of the workflow in the database.
        """
        workflow_code = self._meta.get('workflowCode')
        if not workflow_code:
            self.log(LogLevel.WARNING,
                     "Cannot update workflow lastRunAt: missing workflow code")
            return

        try:
            await temporal_workflow.execute_local_activity(
                GqlActivities.update_workflow_last_run_at,
                args=[workflow_code],
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
            )
            self.log(LogLevel.DEBUG,
                     f"Updated lastRunAt for workflow {workflow_code}")
        except Exception as e:
            self.log(LogLevel.WARNING,
                     f"Failed to update workflow lastRunAt: {e}")

    def _get_service_activity_options(self, service, default_activity_options):
        """Get the activity options for a service, considering its __task_queue__ attribute.

        This helper method retrieves the task queue from the service's __task_queue__ attribute
        if it exists, and merges it with the default activity options. This ensures that
        services are executed on their designated task queues while respecting any
        user-provided options.

        Args:
            service (Callable): The service function
            default_activity_options (dict): Default options that may already include user overrides

        Returns:
            dict: The merged activity options with the service's task queue if available
        """
        service_options = {}
        if hasattr(service, '__task_queue__'):
            service_options['task_queue'] = getattr(service, '__task_queue__')
        return merge_configs(default_activity_options, service_options)
