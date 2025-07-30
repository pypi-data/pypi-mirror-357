"""
Utilities for the Workflows Decorator module.
"""

from typing import Optional, Union, Any

from ..events.workflow_event import EventConfig
from .state_definition import StateDefinition
from .category_definition import WorkflowCategoryDefinition


def standardize_events(events: Optional[list[Union[EventConfig, dict, str]]]) -> list[EventConfig]:
    """Standarize the events into EventConfig type."""
    if not events:
        return []
    std_events = []
    for event in events:
        if isinstance(event, EventConfig):
            std_events.append(event)
        elif isinstance(event, dict):
            std_events.append(EventConfig(**event))
        elif isinstance(event, str):
            std_events.append(EventConfig(code=event))
    return std_events


def standardize_states(states: Optional[list[Union[StateDefinition, dict, str]]]) -> list[StateDefinition]:
    """Standarize the states into StateDefinition type."""
    if not states:
        return []
    std_states = []
    for state in states:
        if isinstance(state, StateDefinition):
            std_states.append(state)
        elif isinstance(state, dict):
            std_states.append(StateDefinition(**state))
        elif isinstance(state, str):
            std_states.append(StateDefinition(code=state))
    return std_states


def is_scream_case(s: str) -> bool:
    """Check if a string is in SCREAM_CASE format.

    SCREAM_CASE means:
    - All uppercase letters, numbers and underscores
    - No consecutive underscores
    - Does not start or end with an underscore
    - Has at least one uppercase letter
    """
    if not s:
        return False

    # Check if starts or ends with underscore (quick check)
    if s.startswith('_') or s.endswith('_'):
        return False

    # Check for consecutive underscores (quick string check)
    if '__' in s:
        return False

    # Check if contains only uppercase letters, numbers, and underscores
    if not all(c.isupper() or c.isdigit() or c == '_' for c in s):
        return False

    # Check if has at least one uppercase letter
    if not any(c.isupper() for c in s):
        return False

    return True


def validate_category_code(code: str) -> None:
    """Validate that a category code is in SCREAM_CASE format.

    Args:
        code (str): The category code to validate

    Raises:
        ValueError: If the code is not in SCREAM_CASE format
    """
    if not is_scream_case(code):
        raise ValueError(
            f"Category code '{code}' is not in SCREAM_CASE format. " +
            "Code should be all uppercase with underscores, no consecutive underscores, " +
            "and should not start or end with an underscore."
        )


def to_human_readable(code: str) -> str:
    """Transform a SCREAM_CASE string to a human-readable string.

    Example: "FREQUENCY_MONITOR" -> "Frequency monitor"

    Args:
        code (str): The SCREAM_CASE string to transform

    Returns:
        str: The human-readable string
    """
    words = code.split('_')
    result = ' '.join(word.lower() for word in words)
    return result[0].upper() + result[1:] if result else result


def standardize_categories(categories: list[Any]) -> list[WorkflowCategoryDefinition]:
    '''
    Standardizes a list of categories to WorkflowCategoryDefinition objects

    Validates that category codes are in SCREAM_CASE format.
    If a name is not provided, it will be generated from the code in human-readable format.

    Args:
        categories (list[Any]): List of categories as strings, dicts, or WorkflowCategoryDefinition objects

    Returns:
        list[WorkflowCategoryDefinition]: List of standardized WorkflowCategoryDefinition objects

    Raises:
        ValueError: If a category is invalid
    '''
    result: list[WorkflowCategoryDefinition] = []
    for category in categories:
        if isinstance(category, str):
            # If just a string code, validate and create a WorkflowCategoryDefinition
            code = category
            validate_category_code(code)
            name = to_human_readable(code)
            result.append(WorkflowCategoryDefinition(code=code, name=name))
        elif isinstance(category, dict):
            # If a dict, create a WorkflowCategoryDefinition with the provided values
            code = category.get('code')
            if not code:
                raise ValueError(f"Category must have a 'code': {category}")

            validate_category_code(code)

            # If name not provided, generate from code
            name = category.get('name')
            if not name:
                name = to_human_readable(code)

            description = category.get('description')
            result.append(WorkflowCategoryDefinition(
                code=code, name=name, description=description))
        elif isinstance(category, WorkflowCategoryDefinition):
            # If already a WorkflowCategoryDefinition, validate the code
            validate_category_code(category.code)

            # If no name was provided, generate one from the code
            if not category.name:
                # Create a new instance with the generated name
                result.append(WorkflowCategoryDefinition(
                    code=category.code,
                    name=to_human_readable(category.code),
                    description=category.description
                ))
            else:
                # Just add it as is
                result.append(category)
        else:
            raise ValueError(
                f"Invalid category type: {type(category)}. Expected string, dict, or WorkflowCategoryDefinition.")
    return result
