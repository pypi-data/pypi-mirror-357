"""
Create the Workflow Handler Base class that will be used by
the WorkflowHandler and PluginMixins.

This class would include the init and basic methods for others
to use.
"""
from abc import ABC
from typing import Any, Callable, Dict, Union
from pygqlc import GraphQLClient

from valiotworkflows.service_handler_base import LogFunctionType
from valiotworkflows.workflows.decorator.workflow_definition import WorkflowDefinition

# For update_progress method
UpdateProgressType = Callable[[int, bool], None]

# For heartbeat method
HeartbeatType = Callable[[Any], None]  # You can replace Any with a more specific type if known

# For send_event method
SendEventType = Callable[[str, Dict[Any, Any]], None]


class WorkflowHandlerBase(ABC):  # pylint: disable=R0903
    """Base class for the WorkflowHandler and PluginMixins.
    It exposes the public methods and private attributes that can
    be used by the WorkflowHandler and PluginMixins.

    Attributes
    ----------
    _context : Union[dict, None]
        The context of the workflow at the time of the service start
    _event : dict
        The event that triggered the service, along with it's payload
    _meta : dict
        Useful metadata of the workflow, like the workflowRunId, stateRunId, serviceId, etc
    _gql : GraphQLClient
        The GraphQLClient instance to be used by the WorkflowHandler and PluginMixins

    Methods
    -------
    update_progress : fn(progress: int, heartbeat: bool = True) -> None
        Updates the progress of the service at the corresponding GraphQL
            serviceRun (and sends a heartbeat if needed)

        Examples:
            >>> handler.update_progress(50) # updates the progress to 50% and sends a heartbeat
            >>> handler.update_progress(50, False) # updates the progress to 50% and DOES NOT
                send a heartbeat
    heartbeat : fn(data: Any) -> None
        Sends a heartbeat to the workflow run at temporal to avoid the service being
        cancelled due to inservice

        Examples:
            >>> handler.heartbeat("I'm alive!") # sends a heartbeat with the string "I'm alive!"
            >>> handler.heartbeat({"foo": "bar"}) # sends a heartbeat with the dict {"foo": "bar"}
            >>> handler.heartbeat(123) # sends a heartbeat with the int 123
            >>> handler.heartbeat() # sends a heartbeat with an empty payload

    log : fn(level: LogLevel, message: Union[str, dict], extra: dict = {}) -> None
        Logs a message with the corresponding level and extra fields
        Note: This method will use the LOGGING_STYLE env var to decide which logger to use.

        Examples:
            >>> handler.log(LogLevel.INFO, "Starting service 1") # logs the string 
                "Starting service 1" with the INFO level
            >>> handler.log(LogLevel.INFO, "Starting service 1", {"foo": "bar"}) 
                # logs the string "Starting service 1" with the INFO level and the
                extra fields {"foo": "bar"}
            >>> handler.log(LogLevel.WARNING, "Starting service 1", {"foo": "bar"}) 
                # logs the string "Starting service 1" with the WARNING level and
                the extra fields {"foo": "bar"}

    TODO documentation methods
    -------
    run_service
    run_parallel_services
    TODO context managing methods
    -------
    enter_state

    TODO general methods:
    -------

    run_child_workflow : 🔥 run a child workflow and wait for it to finish, get the result

    send_event(handle, event) : 🔥 send an event to a workflow based on the workflow handle or run id

    update_progress : 🚼 Can be implemented via plugins

    run : ⬇️ run either a service or a workflow, get the result

    start : ⬇️ start a service or a workflow but don't wait for it to finish,
        get the service/workflow handle instead

    wf_handle.send_event : ⬇️ send an event to a workflow based on the workflow handle or run id

    start_service : ⬇️ start a service but don't wait for it to finish, get the service handle
        instead

    start_child_workflow : ⬇️ start a workflow but don't wait for it to finish, get the workflow
        handle instead

    peek_event : ⬇️ NON-BLOCKING. Check if an event was received at the current workflow without
        consuming it

    flush_events : ⬇️ Flush all events received at the current workflow

    continue_as_new : ⬇️ Finishes current workflow and starts a new one with the same workflow id,
        input, context and options

    should_continue_as_new : ⬇️ Check if the current workflow should continue as new, given the
        size of it's history

    was_cancelled : ⬇️ Check if the current workflow received a cancellation signal

    is_cancellation(error) : ⬇️ Check if an error is a cancellation error

    child.cancel : ⬇️ Cancel the current workflow

    child.terminate : ⬇️ Terminate the current workflow

    set_valid_events : ✅ set the valid events for the current workflow
        (MAYBE AT WORKFLOW DECORATOR LEVEL)

    wait_for_event : ✅ BLOCKING. wait for an event to be received at the current workflow

    wait_for_any_event : ✅ BLOCKING. wait for any event to be received at the current workflow

    enter_state(state_name, exit_with=list[Event]) : ✅ Enter a state in the current workflow,
        and exit with the specified events

    event_received : ✅ NON-BLOCKING. Check if an event was received at the current workflow

    TODO gql reporting methods
    -------
    _
    """
    _context: Union[dict, None] = {}
    _event: dict = {}
    _meta: dict = {} # workflow run id, state run id, service id, temporal id, etc
    # Initialize a GraphQLClient instance for the ServiceHandler and Plugins to use
    _gql: GraphQLClient
    # ServiceHandler public methods:
    update_progress: UpdateProgressType = lambda *args: None
    heartbeat: HeartbeatType = lambda *args: None
    send_event: SendEventType = lambda *args: None
    log: LogFunctionType = lambda *args: None  # type: ignore
    # Include the definition here
    _defn: WorkflowDefinition


    def __init__(self):
        self._gql = GraphQLClient()

    # MAKE THE DEFN A PROPERTY SO IT CAN INCLUDE ALSO A MINOR DOCUMENTATION OF THE ATTRIBUTE
    @property
    def defn(self) -> WorkflowDefinition:
        """Return the Workflow Definition associated to the Workflow running."""
        return self._defn

    @defn.setter
    def defn(self, value: WorkflowDefinition) -> None:
        """Set the Workflow Definition associated to the Workflow running."""
        self._defn = value

    # make definition = defn
    definition = defn


class WorkflowHandle:  # pylint: disable=R0903
    """
    A handle to a running service or workflow.
    It allows to interact with the running service or workflow,
    like updating the progress, sending a heartbeat, etc.

    Attributes
    ----------
    _context : Union[dict, None]
    _meta : dict
    _gql : GraphQLClient

    Methods
    -------

    send_event

    get_state

    join # AKA: wait_until_completed / cancelled

    cancel

    terminate

    """
