"""
ServiceHandler class. The main class with utilities for
the entire service implementation on the workflows.
"""
# Import necessary modules and libraries
from typing import (
    Generic, TypeVar, Union, Optional, Iterable, Any
)
import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from temporalio import activity as temporalio_activity
from valiotlogging import LogLevel, log

from .service_handler_base import ServiceHandlerBase
from .utils import get_current_utc_date, get_own_token_id
from .utils.compressor_mixin import CompressorMixin
from .mutations import UPDATE_PROGRESS, SEND_WORKFLOW_RUN_EVENT
from .redis import ValiotRedisClient, get_valiot_redis_client_for

T = TypeVar('T')


class ServiceHandler(Generic[T], ServiceHandlerBase, CompressorMixin):  # pylint: disable=R0902
    """Utility class to be used by the services.

    Attributes
    ----------
    _context : Union[dict, None]
        The context of the workflow at the time of the service start
    _event : dict
        The event that triggered the service, along with it's payload
    _meta : dict
        Useful metadata of the workflow, like the workflowRunId, stateRunId, serviceId, etc
    _lifecycle : str
        The expected lifecycle for the service
    _updated_context : dict
        The context updates to be sent back to the workflow after the service finishes
    _exit_event : dict
        The exit event of the service, if any (default: ON_INVOCATION_DONE)
    _gql : GraphQLClient
        The GraphQLClient instance to be used by the ServiceHandler and PluginMixins
    r : ValiotRedisClient
        The ValiotRedisClient instance to be used by the ServiceHandler and PluginMixins
    update_progress : fn(progress: int, heartbeat: bool = True) -> None
        Updates the progress of the service at the corresponding GraphQL
        serviceRun (and sends a heartbeat if needed)

        Examples:
            >>> handler.update_progress(50) # updates the progress to 50% and sends a heartbeat
            >>> handler.update_progress(50, False) # updates the progress to 50% and
                DOES NOT send a heartbeat
    heartbeat : fn(data: Any) -> None
        Sends a heartbeat to the workflow run at temporal to avoid the service being
        cancelled due to inactivity

        Examples:
            >>> handler.heartbeat("I'm alive!") # sends a heartbeat with the string "I'm alive!"
            >>> handler.heartbeat({"foo": "bar"}) # sends a heartbeat with the dict {"foo": "bar"}
            >>> handler.heartbeat(123) # sends a heartbeat with the int 123
            >>> handler.heartbeat() # sends a heartbeat with an empty payload
    update_context : fn(data: dict) -> None
        Batches a request to update the context of the workflow at the corresponding workflowRun.
        Note: The context will be updated at the end of the service, not at the time of the call.
        Note 2: This method will merge the context updates with the existing context, not
            replace it.

        Examples:
            >>> handler.update_context({"foo": "bar"}) # updates the context with the dict
                {"foo": "bar"}
            >>> handler.update_context({"foo": "bar", "baz": "qux"}) # updates the context
                with the dict {"foo": "bar", "baz": "qux"}
    exit_with_event : fn(event: str, payload: dict = {}) -> None
        Request the service to exit with an specific event other than ON_INVOCATION_DONE,
            and optionally a payload.
        Note: The custom event will be sent at the end of the service's body, not at the
            time of the call.

        Examples:
            >>> handler.exit_with_event("SKIP") # exits the service with the event "SKIP"
                and an empty payload
            >>> handler.exit_with_event("SKIP", {"foo": "bar"}) # exits the service with
                the event "SKIP" and the payload {"foo": "bar"}
    send_event : fn(event: str, payload: dict = {}) -> None
        Sends an event to the workflow at the corresponding workflowRun
        Note: This method WILL send the event at the time of the call, not at the end of
            the service's body.

        Examples:
            >>> handler.send_event("HIGH_TEMP") # sends the event "HIGH_TEMP" with an empty payload
            >>> handler.send_event("HIGH_TEMP", {"value": 75}) # sends the event "HIGH_TEMP"
                with the payload {"value": 75}
    log : fn(level: LogLevel, message: Union[str, dict], extra: dict = {}) -> None
        Logs a message with the corresponding level and extra fields
        Note: This method will use the LOGGING_STYLE env var to decide which logger to use.

        Examples:
            >>> handler.log(LogLevel.INFO, "Starting service 1")
                # logs the string "Starting service 1" with the INFO level
            >>> handler.log(LogLevel.INFO, "Starting service 1", {"foo": "bar"})
                # logs the string "Starting service 1" with the INFO level
                # and the extra fields {"foo": "bar"}
            >>> handler.log(LogLevel.WARNING, "Starting service 1", {"foo": "bar"})
                # logs the string "Starting service 1" with the WARNING level
                # and the extra fields {"foo": "bar"}
    compress : fn(obj: Any, serializer: Optional[Callable[[Any], str]] = None) -> str
        Compress the given object into a compressed bytes object.
        The compression is done using zlib.

        Args:
            obj (Any): The object to compress and encode.
            serializer (Optional[Callable[[Any], str]]): Custom serializer function.
                If None, uses orjson.dumps. Defaults to None.

        Returns:
            str: The compressed and encoded bytes object (base64).

        Examples:
            >>> handler.compress({"foo": "bar"}) # Basic compression
            >>> handler.compress(user, custom_user_serializer) # Custom serializer
    decompress : fn(compressed_encoded_obj: str, deserializer: Optional[Callable[[str], Any]] = None) -> Any
        Decompress the given compressed and encoded object into the original object.
        The decompression is done using zlib.

        Args:
            compressed_encoded_obj (str): The compressed and encoded bytes object (base64).
            deserializer (Optional[Callable[[str], Any]]): Custom deserializer function.
                If None, uses orjson.loads. Defaults to None.

        Returns:
            Any: The original object.

        Examples:
            >>> handler.decompress(compressed_str) # Basic decompression
            >>> handler.decompress(compressed_str, custom_user_deserializer) # Custom deserializer
    """
    # Initialize a ThreadPoolExecutor instance
    input: T = None  # type: ignore
    executor = ThreadPoolExecutor()
    # Valiot Redis client utilities:
    # not optional to avoid type errors and having to assert every time we use it:
    r: ValiotRedisClient
    is_redis_available: bool

    def __init__(
        self,
        context: Union[dict, None],
        event: dict,
        meta: dict,
        lifecycle: Optional[str] = None,
        input: T = None  # pylint: disable=W0622 # type: ignore
    ) -> None:
        """Initialize an ServiceHandler instance.

        Args:
            context (Union[dict, None]):
                The context of the workflow at the time of the service start.
            event (dict): The event that triggered the service, along with it's payload.
            meta (dict): Useful metadata of the workflow, like the workflowRunId, stateRunId,
                serviceId, etc.

        Returns:
            None
        """
        self._context = context
        self._event = event
        self._meta = meta
        self._lifecycle = lifecycle
        self.input = input
        try:
            self.r = get_valiot_redis_client_for(
                meta.get('workflowRunId', '0'))
            self.is_redis_available = True
        except RuntimeError:
            self.is_redis_available = False
            self.r = None  # type: ignore
        # Safely get the current running asyncio event loop
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running event loop
            self._loop = None

        # Get the logger function
        self.log = self.getProcessLoggerFunction(
            workflowRunId=self._meta.get("workflowRunId", ''),
            stateRunId=self._meta.get("stateRunId", 0),
            serviceRunId=self._meta.get("serviceRunId", 0)
        )

    # ! SERVICE / WORKFLOW METHODS: ---------------------------------------------

    def update_progress(self, progress: int, do_heartbeat: bool = True) -> None:
        """Updates the progress of the service at the corresponding GraphQL
        serviceRun (and sends a heartbeat if needed)

        Examples:
            >>> handler.update_progress(50) # updates the progress to 50% and sends a heartbeat
            >>> handler.update_progress(50, False) # updates the progress to 50% and
                DOES NOT send a heartbeat
        """
        if do_heartbeat:
            self.heartbeat({progress})

        if self._loop:
            # If we have an event loop, run in executor
            self._loop.run_in_executor(
                self.executor, self._update_progress_sync, progress)
        else:
            # Otherwise, run synchronously
            self._update_progress_sync(progress)

    def heartbeat(self, *details: Iterable[Any]) -> None:
        """Sends a heartbeat to the workflow run at temporal to avoid the service
            being cancelled due to inactivity

        Examples:
            >>> handler.heartbeat() # sends a heartbeat with an empty payload
            >>> handler.heartbeat("I'm alive!") # sends a heartbeat with the string "I'm alive!"
            >>> handler.heartbeat({"foo": "bar"}) # sends a heartbeat with the dict {"foo": "bar"}
            >>> handler.heartbeat(123) # sends a heartbeat with the int 123
        """
        temporalio_activity.heartbeat(*details)

    def update_context(self, new_context: dict[Any, Any], overwrite_all: bool = False) -> None:
        """Batches a request to update the context of the workflow at the corresponding workflowRun.

        IMPORTANT: ONLY AVAILABLE for `workflows_studio_service` invocations.

        For `static_workflow_service` and `custom_service` invocations,
        please call the `await update_workflow_context(...)` method
        from the `WorkflowHandler` instance.

        Note: The context will be updated at the end of the service, not at the time of the call.
        Note 2: This method will merge the context updates with the existing context,
            not replace it.

        Examples:
            >>> handler.update_context({"foo": "bar"})
                # updates the context with the dict {"foo": "bar"}
            >>> handler.update_context({"foo": "bar", "baz": "qux"})
                # updates the context with the dict {"foo": "bar", "baz": "qux"}
        """
        if overwrite_all or not self._updated_context:
            self._updated_context = new_context
        else:
            self._updated_context = {
                **self._updated_context,
                **new_context
            }

    def exit_with_event(self, event_name: str, payload: Optional[dict] = None) -> None:
        """Request the service to exit with an specific event other
        than ON_INVOCATION_DONE, and optionally a payload.
        Note: The custom event will be sent at the end of the service's body,
        not at the time of the call.



        Examples:
            >>> handler.exit_with_event("SKIP")
                # exits the service with the event "SKIP" and an empty payload
            >>> handler.exit_with_event("SKIP", {"foo": "bar"})
                # exits the service with the event "SKIP" and the payload {"foo": "bar"}
        """
        self._exit_event = {
            "event": event_name,
            "payload": payload
        }

    def send_event(self, event_code: str, payload: Optional[dict] = None) -> None:
        """Sends an event to the workflow at the corresponding workflowRun
        Note: This method WILL send the event at the time of the call,
            not at the end of the service's body.

        Args:
            event_code (str): The code of the event catalog to send ("CONFIRM", "HIGH_TEMP", etc).
            payload (dict, optional): The payload to attach with the event. Defaults to {}.

        Examples:
            >>> handler.send_event("HIGH_TEMP")
                # sends the event "HIGH_TEMP" with an empty payload
            >>> handler.send_event("HIGH_TEMP", {"value": 75})
                # sends the event "HIGH_TEMP" with the payload {"value": 75}
        """
        if self._loop:
            # If we have an event loop, run in executor
            self._loop.run_in_executor(
                self.executor, self._send_workflow_run_event_sync,
                event_code, payload
            )
        else:
            # Otherwise, run synchronously
            self._send_workflow_run_event_sync(event_code, payload)

    def _build_response(self):
        """Build the response to be returned after the service is done.

        Returns:
            dict: A dictionary containing actions and payload.
        """
        response = {"actions": {}}
        if self._updated_context:
            response["actions"]["assign"] = {
                "updatedContext": self._updated_context}
        if self._exit_event:
            response["actions"]["exit"] = self._exit_event
        else:
            # ensure the exit event it's explicitly set to the default behaviour: ON_INVOCATION_DONE
            response["actions"]["exit"] = {
                "event": "ON_INVOCATION_DONE", "payload": {}}
        return response

    def build_response(self, return_value: Any) -> dict:
        """Builds a complete response with the return value and service name.

        Args:
            return_value (Any): The value to be returned in the response payload.

        Returns:
            dict: A complete response dictionary containing actions, payload, and service name.
        """
        response = self._build_response()
        response['payload'] = return_value
        response['_service'] = self._meta.get('serviceName', '')
        return response

    # ! PRIVATE METHODS: ---------------------------------------------

    def _update_progress_sync(self, progress: int) -> None:
        """Synchronously update the progress by making a GraphQL mutation.

        Args:
            progress (int): The progress to be updated.

        Returns:
            None
        """
        self._gql.mutate(UPDATE_PROGRESS, variables={
            "serviceRunId": self._meta.get("serviceRunId"),
            "progress": progress
        })

    def _send_workflow_run_event_sync(
        self,
        event_code: str,
        payload: Optional[dict] = None
    ) -> None:
        """Synchronously send an event to the workflow run.

        Args:
            event_code (str): The code of the event catalog to send ("CONFIRM", "HIGH_TEMP", etc).
            payload (dict, optional): The payload to attach with the event. Defaults to {}.

        Returns:
            None
        """
        own_token_id = get_own_token_id()
        variables = {
            "workflowRunId": self._meta.get("workflowRunId"),
            "eventCode": event_code,
            "emitterTokenId": own_token_id,
            "payload": json.dumps(payload if payload else {})
        }
        self._gql.mutate(SEND_WORKFLOW_RUN_EVENT, variables=variables)

    def get_process_logger_function(
        self,
        workflowRunId=0,  # pylint: disable=C0103
        stateRunId=0,  # pylint: disable=C0103
        serviceRunId=0  # pylint: disable=C0103
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
        st_run = str(stateRunId).zfill(5)
        srv_run = str(serviceRunId).zfill(5)
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
                        f'[D={date}/WfR={wf_run}/StR={st_run}/SvR={srv_run}] - {msg}',
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
                    'stateRunId': st_run,
                    'serviceRunId': srv_run,
                    'workflow': workflow_code,
                    **extra_params
                })
        return formatted_log

    # Create a call for the same getProcessLoggerFunction
    getProcessLoggerFunction = get_process_logger_function
