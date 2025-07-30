"""
Include the ServiceHandlerBase class, as the abstract base
class for the ServiceHandler one
"""
from typing import Any, Callable, Dict, Union, Optional, Protocol
from valiotlogging import LogLevel
from pygqlc import GraphQLClient
from .redis import ValiotRedisClient


# For update_progress method
UpdateProgressType = Callable[[int, bool], None]

# For heartbeat method
# You can replace Any with a more specific type if known
HeartbeatType = Callable[[Any], None]

# For update_context method
# You can replace Any with a more specific type if known
UpdateContextType = Callable[[Any], None]

# For exit_with_event method
ExitWithEventType = Callable[[str, Dict[Any, Any]], None]

# For send_event method
SendEventType = Callable[[str, Dict[Any, Any]], None]


class LogFunctionType(Protocol):  # pylint: disable=R0903
    """Type for the log method"""

    def __call__(
        self,
            level: LogLevel,
            message: str,
            extra: Optional[Dict[str, Any]] = None
    ) -> None:
        ...


class ServiceHandlerBase:  # pylint: disable=R0903
    """Base class for the ServiceHandler and PluginMixins.
    It exposes the public methods and private attributes
    that can be used by the ServiceHandler and PluginMixins.

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
    update_progress : fn(progress: int, heartbeat: bool = True) -> None
        Updates the progress of the service at the corresponding GraphQL serviceRun
        (and sends a heartbeat if needed)

        Examples:
            >>> handler.update_progress(50) # updates the progress to 50% and sends a heartbeat
            >>> handler.update_progress(50, False) # updates the progress to 50% and DOES NOT
                send a heartbeat
    heartbeat : fn(data: Any) -> None
        Sends a heartbeat to the workflow run at temporal to avoid the service being cancelled
        due to inservice

        Examples:
            >>> handler.heartbeat("I'm alive!") # sends a heartbeat with the string "I'm alive!"
            >>> handler.heartbeat({"foo": "bar"}) # sends a heartbeat with the dict {"foo": "bar"}
            >>> handler.heartbeat(123) # sends a heartbeat with the int 123
            >>> handler.heartbeat() # sends a heartbeat with an empty payload
    update_context : fn(data: dict) -> None
        Batches a request to update the context of the workflow at the corresponding workflowRun.
        Note: The context will be updated at the end of the service, not at the time of the call.
        Note 2: This method will merge the context updates with the existing context, not replace
            it.

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
                # logs the string "Starting service 1" with the INFO level and
                # the extra fields {"foo": "bar"}
            >>> handler.log(LogLevel.WARNING, "Starting service 1", {"foo": "bar"})
                # logs the string "Starting service 1" with the WARNING level and
                # the extra fields {"foo": "bar"}
    """
    _context: Union[dict, None] = {}
    _event: dict = {}
    _meta: dict = {}
    _lifecycle: Optional[str] = None
    _updated_context: Optional[dict] = None
    _exit_event: Optional[dict] = None
    # Initialize a GraphQLClient instance for the ServiceHandler and Plugins to use
    _gql: GraphQLClient = GraphQLClient()
    # Valiot Redis client utilities:
    r: Optional[ValiotRedisClient] = None
    # ServiceHandler public methods:
    update_progress: UpdateProgressType = lambda *args: None
    heartbeat: HeartbeatType = lambda *args: None
    update_context: UpdateContextType = lambda *args: None
    exit_with_event: ExitWithEventType = lambda *args: None
    send_event: SendEventType = lambda *args: None
    log: LogFunctionType = lambda *args: None
