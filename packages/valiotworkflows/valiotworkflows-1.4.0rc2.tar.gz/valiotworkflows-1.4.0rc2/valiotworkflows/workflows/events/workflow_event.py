"""
Definition of the class for the Workflow Event
"""
from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass
class EventConfig:
    """Event Configuration Schema.

    For the MaxSize, we can use -1 to indicate no limit, or any positive integer to limit the size.
    """
    code: str
    payload_schema: dict = field(default_factory=dict)
    kind: Optional[Literal["SINGLE", "QUEUE"]] = 'QUEUE'  # 'SINGLE' or 'QUEUE'
    # -1 means no limit, any positive integer is allowed
    max_size: Optional[int] = -1


@dataclass
class WorkflowEvent:
    """Workflow Event Schema.

    Include the type of the event, the payload, the emitterTokenId and the workflowRunEventId.
    """
    # {'type': 'FINISH', 'payload': {'blabla': True, 'name': 'baruc'},
    #  'emitterTokenId': '227', 'workflowRunEventId': '2006'}
    type: str
    payload: dict = field(default_factory=dict)
    emitterTokenId: Optional[str] = None  # pylint: disable=C0103
    workflowRunEventId: Optional[str] = None  # pylint: disable=C0103
