"""
Definition of the state definition for the Workflow Decorator.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkflowCategoryDefinition:
    """Dataclass for a workflow category definition"""
    code: str  # Unique machine-readable code
    name: str  # Human-readable name
    description: Optional[str] = None
