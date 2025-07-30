"""This module contains a Python workflow class for managing and executing
workflows in Temporal. It provides methods for setting up workflows, running
them, and handling their execution.

Classes:
    ValiotPythonWorkflow: A Python workflow class for managing and executing workflows.
"""
import asyncio
from typing import Optional, Sequence, Callable, Type, Any, TYPE_CHECKING
import pydash as __  # pylint: disable=W0611
from valiotlogging import log, LogLevel
# Temporal imports
from temporalio import workflow as temporal_workflow
from temporalio.common import RawValue
from temporalio.exceptions import FailureError

from .decorator.workflow_definition import WorkflowDefinition
from .decorator.utils import standardize_events

# Local imports
from .events import WorkflowEvent, EventConfig
from .gql_activities import GqlActivities

# Import WorkflowHandler only for type checking
if TYPE_CHECKING:
    from ..workflows.workflow_handler import WorkflowHandler


@temporal_workflow.defn(dynamic=True, sandboxed=False)
class ValiotPythonWorkflow:
    """A Python workflow class for managing and executing workflows.

    This class is responsible for defining and running Python workflows in Temporal. It allows
    setting up workflows, running them, and handling their execution.

    Methods:
        set_workflows: A class method to set the workflows for the ValiotPythonWorkflow class.
        run: A method to execute the specified workflow.
    """
    _selected_workflow: Callable[..., Any]
    _workflows: dict[str, Callable]
    _workflow_run_id: Optional[str] = None
    # Handler for workflow execution context and logging
    _handler: Optional['WorkflowHandler'] = None

    def __init__(self) -> None:
        """Initialize a new instance of the ValiotPythonWorkflow class."""
        self._selected_workflow = None  # type: ignore
        self._event_configs: list[EventConfig] = []
        self._events_queue = asyncio.Queue()
        self._workflow_run_id = None
        self._handler = None  # Will be set during run() method

    @classmethod
    def set_workflows(
        cls: Type["ValiotPythonWorkflow"],
        workflows: dict[str, Callable]
    ) -> Type["ValiotPythonWorkflow"]:
        """Set the workflows for the ValiotPythonWorkflow class.

        Args:
            workflows (dict[str, Callable[..., WORKFLOW]]): A dictionary containing workflow codes
                mapped to their corresponding workflow functions.

        Returns:
            Type["ValiotPythonWorkflow"]: The modified class with the set workflows.
        """
        # Just set the workflows as the internal value
        setattr(cls, "_workflows", workflows)
        return cls

    async def update_workflow_run_event(
        self,
        event_id: Optional[str | int],
        workflow_run_id: Optional[str | int] = None,
        is_successful: bool = True,
        error_messages: Optional[list[dict[str, str]]] = None,
        logger: Callable = log,
        run_in_background: bool = False
    ) -> None:
        """Update a workflow run event with the workflow run ID and success/error status.

        Args:
            event_id: The ID of the event to update
            workflow_run_id: Override for the workflow run ID. This is useful for
                             handling events that were incorrectly routed to this workflow.
                             When None (default), uses self._workflow_run_id.
                             When set to 0 or "", it will mark the event as failed without
                             attaching any workflow run ID.
            is_successful: Whether the event was successfully processed
            error_messages: Optional list of error messages if unsuccessful
            logger: Logging function to use for error reporting
            run_in_background: When True, starts the activity but doesn't await its completion.
                               Useful for event updates that shouldn't block workflow execution.
        """
        if not event_id:
            logger(LogLevel.WARNING,
                   "Cannot update workflow run event: missing event_id")
            return

        # Use provided workflow_run_id or default to the instance's workflow_run_id
        effective_workflow_run_id = (
            workflow_run_id
            if workflow_run_id is not None
            else self._workflow_run_id
        )

        activity_args = [
            event_id,
            effective_workflow_run_id,
            is_successful,
            error_messages
        ]

        try:
            # Choose method based on whether to run in background or not
            method = (
                temporal_workflow.start_local_activity_method
                if run_in_background
                else temporal_workflow.execute_local_activity_method
            )

            # Execute the appropriate method
            activity_handle = method(
                GqlActivities.update_workflow_run_event,
                args=activity_args,
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
            )

            # Await if using the execute method (blocking execution)
            if not run_in_background:
                await activity_handle
        except Exception as e:
            error_msg = f"Failed to update workflow run event {event_id}: {e}"
            logger(LogLevel.WARNING, error_msg)

    async def create_workflow_run_event(
        self,
        event_code: str,
        payload: Optional[dict[str, Any]] = None,
        emitter_token_id: Optional[str | int] = None,
        workflow_run_id: Optional[str | int] = None,
        logger: Callable = log
    ) -> None:
        """Create a workflow run event in GraphQL for internal events (always runs in background).

        This method is used to record events that are generated internally (via Temporal signals)
        and don't come from GraphQL, ensuring all events are properly tracked.

        Args:
            event_code: The code of the event to create
            payload: The payload data for the event
            emitter_token_id: Token ID of the event emitter, if available
            workflow_run_id: Override for the workflow run ID. When None (default),
                            uses self._workflow_run_id
            logger: Logging function to use for error reporting
        """
        if not self._workflow_run_id and not workflow_run_id:
            logger(LogLevel.WARNING,
                   "Cannot create workflow run event: missing workflow_run_id")
            return

        # Use provided workflow_run_id or default to the instance's workflow_run_id
        effective_workflow_run_id = (
            workflow_run_id
            if workflow_run_id is not None
            else self._workflow_run_id
        )

        # Default to empty dict if payload is None
        effective_payload = payload or {}

        activity_args = [
            effective_workflow_run_id,
            event_code,
            effective_payload,
            emitter_token_id
        ]

        try:
            # Always run in background to avoid blocking workflow execution
            temporal_workflow.start_local_activity_method(
                GqlActivities.create_workflow_run_event,
                args=activity_args,
                **GqlActivities.DEFAULT_LOCAL_ACTIVITY_OPTIONS
            )
            logger(LogLevel.DEBUG,
                   f"Started creation of workflow run event {event_code} in background")
        except Exception as e:
            error_msg = f"Failed to create workflow run event {event_code}: {e}"
            logger(LogLevel.WARNING, error_msg)

    @temporal_workflow.run
    async def run(self, args: Sequence[RawValue]) -> None:
        """Execute a workflow comming from the passed arguments.

        Args:
            args (Sequence[RawValue]): The sequence of raw values representing the workflow
                arguments.

        Raises:
            RuntimeError: If workflows have not been set for the class.
            TypeError: If payload arguments cannot be parsed as a dictionary.
            ValueError: If the payload does not include a Workflow to execute.
        """
        # Import the WorkflowHandler here to avoid circular imports at the top of the file
        from ..workflows.workflow_handler import WorkflowHandler  # pylint: disable=C0415
        # Evaluate if you have workflows
        if hasattr(self, '_workflows') is False:
            raise RuntimeError(
                "You must pass the workflows to be able to run this." +
                "For this, use the classmethod `set_workflows`."
            )
        # Parse the arguments from this call
        if len(args) != 3:
            raise ValueError(
                "The workflow payload doesn't include the expected arguments. We cannot run it." +
                f"Expected 3 arguments, got {len(args)}."
            )
        try:
            parsed_args = [
                temporal_workflow.payload_converter().from_payload(arg.payload, dict)
                for arg in args
            ]
            [wf_data_arg, wf_init_evt_arg, wf_meta_arg] = parsed_args
        except Exception as e:  # pylint: disable=W0612
            raise TypeError(
                "We cannot parse the payload arguments, since they're not a dict."
            ) from e
        # import json
        # ! log(LogLevel.DEBUG, f"parsed workflow Arguments: \n{json.dumps(parsed_args, indent=2)}")
        # With the arguments, now evaluate if you're looking for this workflow to run.
        if not "workflowCode" in wf_meta_arg:
            raise ValueError(
                "The payload doesn't include a Workflow to execute. We cannot run it")
        workflow_code = wf_meta_arg["workflowCode"]
        # Using pydash, found the Workflow in the workflows previously set. If the Workflow is not
        # here, just print a warning message and return Nothing. Otherwise, run the workflow.
        if workflow_code not in self._workflows:
            raise FailureError("This Worker doesn't have the workflow " +
                               f"{workflow_code}, so it cannot be executed.")
        # assign current workflow:
        self._selected_workflow = self._workflows[workflow_code]
        self.set_valid_events()  # store the valid events for this workflow (from the decorator)
        # parse the init event
        wfrun_event: dict = wf_init_evt_arg.get("event", {})
        init_event = WorkflowEvent(
            type="INIT",
            emitterTokenId=wfrun_event.get("emitterTokenId", None),
            workflowRunEventId=wfrun_event.get("id", None),
            payload=wfrun_event.get("payload", {})
        )
        # Before running the workflow, instance an unique handler for this execution
        self._handler = WorkflowHandler(
            self, wf_data_arg, wf_init_evt_arg, wf_meta_arg)
        # Include the definition of the workflow in the handler
        self._handler.defn = self._selected_workflow.__vw_defn__
        self._handler.log(
            LogLevel.INFO, f"Running workflow {workflow_code}...")
        # TODO: maybe we should skip this if it's a continue_as_new:
        self._workflow_run_id = await self._handler._create_workflow_run()  # pylint: disable=W0212
        await self._handler._update_workflow_last_run_at()  # pylint: disable=W0212

        # report the workflow run id to graphQL
        await self.update_workflow_run_event(
            init_event.workflowRunEventId,
            logger=self._handler.log
        )

        try:
            workflow_result = await self._selected_workflow({}, init_event, self._handler)
        except Exception as e:
            if isinstance(e, temporal_workflow.ContinueAsNewError):
                self._handler.log(LogLevel.WARNING,
                                  f"Workflow {workflow_code} is continuing as new...")
                raise  # Re-raise the ContinueAsNewError exception, as God intended
            self._handler.log(LogLevel.ERROR,
                              f"Workflow {workflow_code} failed with error: {e}")
            workflow_result = None
        # Finish the workflow execution
        # TODO: should we run this during handler.continue_as_new? maybe not,
        # if it's itended to be seen as the same workflow
        await self._handler._finish_workflow_run()  # pylint: disable=W0212
        self._handler.log(
            LogLevel.INFO,
            f"\t> Finished running workflow {workflow_code} with wfRun {self._workflow_run_id}..."
        )
        return workflow_result

    # ! handles all the events (signals for temporal) that the workflow can receive
    @temporal_workflow.signal(name='workflow:event')
    async def signal(self, incoming_event_dict: Optional[dict[str, Any]] = None) -> None:
        """Handles the signal events that the workflow can receive."""
        if not self._selected_workflow or not self._handler:
            raise RuntimeError("No workflow is currently running.")
        if not incoming_event_dict:
            incoming_event_dict = {}
        # validate if this is an expected event
        available_events = self._event_configs
        incoming_event = WorkflowEvent(**incoming_event_dict)
        incoming_event_config: Optional[EventConfig] = __.find(
            available_events, lambda evt: evt.code == incoming_event.type)
        if not incoming_event_config:
            self._handler.log(
                LogLevel.ERROR,
                f"The incoming event ({incoming_event.type}) is not" +
                " expected by the current workflow."
            )
            # If we have workflowRunEventId, update it with error message
            if incoming_event.workflowRunEventId:
                await self.update_workflow_run_event(
                    incoming_event.workflowRunEventId,
                    # Special case: 0 means no workflow run ID since it's not for this workflow
                    workflow_run_id=0,
                    is_successful=False,
                    error_messages=[
                        {"field": "event",
                            "message": "Event not expected by this workflow"}
                    ],
                    logger=self._handler.log
                )
            return

        self._handler.log(
            LogLevel.INFO, f"Received external event {incoming_event}")

        # If the event has a workflowRunEventId, update it with the workflow run ID
        if incoming_event.workflowRunEventId:
            # Update the event in the background without waiting for completion
            await self.update_workflow_run_event(
                incoming_event.workflowRunEventId,
                is_successful=True,
                run_in_background=True,  # Don't block workflow execution
                logger=self._handler.log
            )
        # If the event doesn't have a workflowRunEventId, create a new event record in GraphQL
        # This happens when events are sent directly via temporal signals (not through GraphQL)
        elif self._workflow_run_id:
            # Record this internal event in GraphQL for tracking purposes
            await self.create_workflow_run_event(
                event_code=incoming_event.type,
                payload=incoming_event.payload or {},
                emitter_token_id=incoming_event.emitterTokenId,
                logger=self._handler.log
            )

        # if the event is a queue event, append it to the queue
        await self._events_queue.put(incoming_event)

    def set_valid_events(self) -> None:
        """Set the valid events that can come from the Workflow Definition
        of the selected workflow.
        """
        if not hasattr(self._selected_workflow, '__vw_defn__'):
            raise RuntimeError(
                "The selected workflow doesn't have any expected events.")
        wf_definition: WorkflowDefinition = self._selected_workflow.__vw_defn__
        self._event_configs: list[EventConfig] = standardize_events(
            wf_definition.events
        )
