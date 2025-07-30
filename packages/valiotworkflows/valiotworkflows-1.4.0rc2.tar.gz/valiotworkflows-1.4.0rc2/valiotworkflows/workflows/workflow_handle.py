"""
Include the implementation of the Workflow Handle
"""
from typing import Any, Optional, Union
from temporalio import workflow as temporal_workflow
from .utils import get_token_id_from_env

# ! TODO: Implement the ApplicationError valiotworkflows exception
# !(to avoid exporting temporalio exceptions to the user)


class WorkflowHandle:
    """The Workflow Handle class that will be used by the
    WorkflowHandler and PluginMixins.

    This method includes:
      - The Workflow Code
      - The Raw Handle
      - The Temporal Workflow Handle

    Having all these things stored here, as we can await for workflows
    and send events to them.
    """

    def __init__(
        self,
        workflow_code: str,
        raw_handle: dict,
        temporal_workflow_handle: Union[
            temporal_workflow.ExternalWorkflowHandle,
            temporal_workflow.ChildWorkflowHandle
        ]
    ):
        self.workflow_code = workflow_code
        self.raw_handle = raw_handle
        self._temporal_workflow_handle = temporal_workflow_handle
        # Extract token_id from environment
        self._emitter_token_id = get_token_id_from_env()

    # make the instance awaitable and return the workflow result:
    def __await__(self) -> Any:
        return self._temporal_workflow_handle.__await__()  # pylint: disable=no-member # type: ignore

    async def send_event(
        self,
        event_code: str,
        payload: Optional[dict] = None
    ) -> Optional[Exception]:
        """Send an event to the workflow.

        Args:
            event_code (str): The event code to send to the workflow.
            payload (Optional[dict]): The payload of the event. Default to None.

        Returns:
          Exception: If there is an error sending the event.
        """
        payload = payload or {}
        arg = {
            "type": event_code,
            "payload": payload,
            "emitterTokenId": self._emitter_token_id,
            "workflowRunEventId": None,
        }
        try:
            await self._temporal_workflow_handle.signal('workflow:event', arg=arg)
        # We'll catch all exceptions here, that's why we use the base Exception
        except Exception as e:  # pylint: disable=W0718
            return e
