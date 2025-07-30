"""
Definition of the state definition for the Workflow Decorator.
"""
from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class StateDefinition:
    """Dataclass for a workflow state definition
    (state type, transitions and invocations it can handle, etc)
    """
    code: str
    name: Optional[str] = None
    type: Literal["normal", "final"] = "normal"  # normal, final
    # TODO: transitions: Optional[list[Union[TransitionDefinition, dict, str]]]

    def __post_init__(self):
        if not self.code:
            raise ValueError("State code is required")
        if self.type not in ["normal", "final"]:
            raise ValueError("State type must be 'normal' or 'final'")
        # set name as code if not provided:
        self.name = self.name or self.code
