"""
This module provides a decorator to turn a regular function into a Valiot workflow.

The `workflow` decorator function takes a `WorkflowDefinition` object and optional
configuration and plugins, and returns a decorator that can be applied to a function
to transform it into a workflow.

Functions decorated with `workflow` will have their name changed to the workflow code,
and will have additional attributes to indicate they are workflows and to store the
workflow definition.
"""
# standard imports
import dataclasses
from typing import Any, Callable, Dict, Optional, Union, Literal, overload
from copy import copy
# package imports
# from ..events.workflow_event import EventConfig
# module imports
from .workflow_definition import WorkflowDefinition
from .utils import standardize_events, standardize_states

ReturnType = Union[Dict[str, Any], None]


@dataclasses.dataclass(init=False)
class TemplateServiceConfig:
    """Add the configuration for the services of a dynamic
    workflow. This configuration lets us know which services
    are mandatory and which are optional.

    - If `required` is True, the service is mandatory, and `default_call`
      should be None. An abstract callable will be added by default that
      raises an error if it is not implemented.
    - If `required` is False, the service is optional, and `default_call`
      should be provided. A simple method that does nothing will be used
      if `default_call` is not provided.
    """
    service_key: str  # The key to use in the dynamic workflow
    required: bool  # If the service is mandatory or not
    # * The default call in case the service is not defined (for optional services)
    default_call: Optional[Callable[..., Any]] = None

    @overload
    def __init__(
        self,
        service_key: str,
        *,
        required: Literal[True],
        default_call: None = None
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        service_key: str,
        *,
        required: Literal[False],
        default_call: Optional[Callable[..., Any]] = None
    ) -> None:
        ...

    def __init__(
        self,
        service_key: str,
        *,
        required: bool,
        default_call: Optional[Callable[..., Any]] = None
    ) -> None:

        if required and default_call is not None:
            raise ValueError(
                f"[CONFIG: {service_key}] The parameter default_call should " +
                "be None if the service is required."
            )
        # Init the parameters
        self.service_key = service_key
        self.required = required
        self.default_call = default_call


@dataclasses.dataclass(init=False)
class TemplateChildWorkflowConfig:
    """Add the configuration for the child workflows of a dynamic
    workflow. This configuration lets us know which child workflows
    are mandatory and which are optional.

    - If `required` is True, the child workflow is mandatory, and `default_call`
      should be None. An abstract callable will be added by default that
      raises an error if it is not implemented.
    - If `required` is False, the child workflow is optional, and `default_call`
      should be provided. A simple method that does nothing will be used
      if `default_call` is not provided.
    """
    workflow_key: str
    required: bool
    default_call: Optional[Callable[..., Any]] = None

    @overload
    def __init__(
        self,
        workflow_key: str,
        *,
        required: Literal[True],
        default_call: None = None
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        workflow_key: str,
        *,
        required: Literal[False],
        default_call: Optional[Callable[..., Any]]
    ) -> None:
        ...

    def __init__(
        self,
        workflow_key: str,
        *,
        required: bool,
        default_call: Optional[Callable[..., Any]] = None
    ) -> None:
        if required and default_call is not None:
            raise ValueError(
                f"[CONFIG: {workflow_key}] The parameter default_call should " +
                "be None if the workflow is required."
            )
        # Init the parameters
        self.workflow_key = workflow_key
        self.required = required
        self.default_call = default_call


@dataclasses.dataclass
class TemplateDefinition:
    """Configuration for dynamic workflows.

    This class defines the configuration for dynamic workflows, including the base code
    and the services and child workflows required.
    The dynamic configuration determines which services are mandatory and which are optional,
    and provides default callables for optional services.

    Attributes:
        code(str): The base code for the dynamic workflow.
        services(list[TemplateServicesConfig]): A list of service configurations, each
            specifying whether the service is mandatory or optional, and providing a
            default callable for optional services.
        child_workflows(list[TemplateChildWorkflowConfig]): A list of child workflow configurations,
            each specifying whether the child workflow is mandatory or optional,
            and providing a default callable for optional child workflows.
    """
    code: str  # The base code for the dynamic workflow
    services: list[TemplateServiceConfig]
    child_workflows: list[TemplateChildWorkflowConfig] = dataclasses.field(
        default_factory=list)


# ================================================================= #
#                   Workflow Decorator                              #
# ================================================================= #

# * NOTE: You can just have definition or dynamic on the same level, NOT BOTH OF THEM.
# * The dynamic is a flag that indicates that the workflow needs a definition
# * to be placed to the callable.
# *
# * The definition is the actual real metadata of the workflow
# * The workflow dynamic is going to create a WorkflowDefinition object with metadata
# * for it. This metadata is going to be used to have something that can be dynamically
# * adjusted


@overload
def workflow(
        definition: WorkflowDefinition,
        *,
        dynamic: bool = False,
        template_defn: None = None,
        task_queue: str = 'default-valiotworkflows-task-queue',
        config: Optional[dict] = None,
        plugins: Optional[list] = None,
) -> Callable:
    ...


@overload
def workflow(
        *,
        dynamic: bool = True,
        template_defn: TemplateDefinition,
        task_queue: str = 'default-valiotworkflows-task-queue',
        config: Optional[dict] = None,
        plugins: Optional[list] = None,
) -> Callable:
    ...


def workflow(
    definition: Optional[WorkflowDefinition] = None,
    *,
    dynamic: bool = False,
    template_defn: Optional[TemplateDefinition] = None,
    task_queue: str = 'default-valiotworkflows-task-queue',
    # TODO: ADD FUNCTIONS FOR THE CONFIG AND PLUGINS
    config: Optional[dict] = None,  # pylint: disable=W0613 # type: ignore
    plugins: Optional[list] = None,  # pylint: disable=W0613 # type: ignore
) -> Callable:
    """
    Turns a regular function into a valiot workflow.

    Args:
        definition(WorkflowDefinition): The definition of the workflow
            (code, name, states, events, ...).
        config(Optional[dict], optional): The default config for the workflow.
            Trigger, schedules, etc. Defaults to None.
        plugins(Optional[list], optional): The plugins to use in the workflow.
            Defaults to None.
    """
    if definition is None and not dynamic:
        raise ValueError(
            "A `@workflow(definition=...)` is required for static workflows")

    if definition is not None and dynamic:
        raise ValueError(
            "A `@workflow(definition=...)` cannot be provided if `@workflow(dynamic=True)`. " +
            "For dynamic workflows, we need to have a Workflow Definition as follows:\n\n" +
            "WorkflowDefinition(\n\t...\n\tworkflow=...\n)\n\n" +
            "using the `workflow` field."
        )
    if template_defn is None and dynamic:
        raise ValueError(
            "A `@workflow(template_defn=...)` is required if `@workflow(dynamic=True)`.")

    # Define the wf_definition
    if not definition and template_defn:
        wf_definition = WorkflowDefinition(
            code="DYNAMIC:"+template_defn.code,
            name="DYNAMIC:"+template_defn.code
        )
        # Create a copy of the definition (ONLY IF IT IS A TEMPLATE)
        wf_definition = copy(wf_definition)
    else:
        wf_definition: WorkflowDefinition = definition  # type: ignore

    # consolidate events into the EventConfig type:
    wf_definition.events = standardize_events(
        wf_definition.events or [])  # type: ignore
    # consolidate states into the StateDefinition type:
    wf_definition.states = standardize_states(
        wf_definition.states or [])  # type: ignore

    def workflow_decorator(function: Callable[..., ReturnType]) -> Callable:
        """Internal decorator for the workflow"""
        # Just change the function name
        function.__name__ = wf_definition.code
        function.__is_workflow__ = True
        function.__is_dynamic__ = dynamic
        function.__dynamic_config__ = template_defn
        function.__vw_defn__ = wf_definition
        function.__task_queue__ = task_queue
        # to allow calling the original function for testing
        function.__wrapped__ = function
        # TODO: the next, is required due to an egg and chicken problem
        # (WorkflowDefinition.workflow vs @workflow(defn=...))
        # to easily keep track of WorkflowDefinition's code to execute:
        wf_definition.workflow = function
        return function
    # And return the decorator
    return workflow_decorator
