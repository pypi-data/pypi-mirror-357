"""
This module defines the WorkflowDefinition dataclass, which represents the structure of a workflow,
including its states, events, and other relevant attributes.
"""
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Literal, Optional, Union, Callable, Any
)
from enum import Enum
from valiotlogging import log, LogLevel
from valiotworkflows.utils import create_copy_func
from valiotworkflows.workflows.workflow_setup import SetupResult
from ..events.workflow_event import EventConfig
from .state_definition import StateDefinition
from .category_definition import WorkflowCategoryDefinition

if TYPE_CHECKING:
    # Define the Setup Function type
    SetupFunction = Callable[['WorkflowDefinition'],
                             Awaitable[tuple[SetupResult, str | None]]]


class WorkflowTrigger(str, Enum):
    """Enum to define the possible triggers for a workflow.
    """
    CONTINUOUS = 'CONTINUOUS'
    ON_DEMAND = 'ON_DEMAND'
    SCHEDULE = 'SCHEDULE'


class ScheduleOverlapPolicy(str, Enum):
    """Controls what happens when a workflow would be started by a schedule but
    one is already running.
    """

    SKIP = 'SKIP'
    """Don't start anything.

    When the workflow completes, the next scheduled event after that time will
    be considered.
    """

    BUFFER_ONE = 'BUFFER_ONE'
    """Start the workflow again soon as the current one completes, but only
    buffer one start in this way.

    If another start is supposed to happen when the workflow is running, and one
    is already buffered, then only the first one will be started after the
    running workflow finishes.
    """

    BUFFER_ALL = 'BUFFER_ALL'
    """Buffer up any number of starts to all happen sequentially, immediately
    after the running workflow completes."""

    CANCEL_OTHER = 'CANCEL_OTHER'
    """If there is another workflow running, cancel it, and start the new one
    after the old one completes cancellation."""

    TERMINATE_OTHER = 'TERMINATE_OTHER'
    """If there is another workflow running, terminate it and start the new one
    immediately."""

    ALLOW_ALL = 'ALLOW_ALL'
    """Start any number of concurrent workflows.

    Note that with this policy, last completion result and last failure will not
    be available since workflows are not sequential."""


class _ServicesDefn:
    """Callable class to define the services for the WorkflowDefinition.
    Allows for easy access to the workflow services like:
    `services.service_name` instead of `services['service_name']`
    """
    _defn_code: str
    _services: dict[str, Callable]

    def __init__(self, _defn_code: str, services: Union[dict[str, Callable], None] = None):
        self._defn_code = _defn_code
        self._services = services or {}

    def __getattr__(self, name: str) -> Callable:
        """Access services with dot notation."""
        # special keywords:
        if name in ('items', 'keys', 'values'):
            return getattr(self._services, name)
        if name in self._services:
            return self._services[name]
        raise AttributeError(
            f"The service '{name}' was not defined for " +
            f"the workflow definition '{self._defn_code}'.\n" +
            f"Available services: {list(self._services.keys())}"
        )

    def __getitem__(self, key: str) -> Callable:
        """Allow dictionary-style access."""
        return self._services[key]

    def __len__(self) -> int:
        return len(self._services)

    def __iter__(self):
        return iter(self._services.values())

    def __str__(self):
        return f"<Services for Workflow '{self._defn_code}': {list(self._services.keys())}>"

    def __repr__(self):
        return self.__str__()


class _ChildWorkflowsDefn:
    """Callable class to define the child workflows for the WorkflowDefinition.
    Allows for easy access to the workflow childs like:
    `child_workflows.workflow_name` instead of `child_workflows['workflow_name']`
    """
    _defn_code: str
    _workflows: dict[str, Callable]

    def __init__(self, _defn_code: str, workflows: Union[dict[str, Callable], None] = None):
        self._defn_code = _defn_code
        self._workflows = workflows or {}

    def __getattr__(self, name: str) -> Callable:
        """Access workflows with dot notation."""
        # special keywords:
        if name in ('items', 'keys', 'values'):
            return getattr(self._workflows, name)
        if name in self._workflows:
            return self._workflows[name]
        raise AttributeError(
            f"The child workflow '{name}' was not defined for" +
            f"the workflow definition '{self._defn_code}'.\n" +
            f"Available workflows: {list(self._workflows.keys())}"
        )

    def __getitem__(self, key: str) -> Callable:
        """Allow dictionary-style access."""
        return self._workflows[key]

    def __len__(self) -> int:
        return len(self._workflows)

    def __iter__(self):
        return iter(self._workflows.values())

    def __str__(self):
        return f"<Child workflows for Workflow '{self._defn_code}': {list(self._workflows.keys())}>"

    def __repr__(self):
        return self.__str__()


@dataclass
class WorkflowDefinition:  # pylint: disable=R0902
    """Dataclass for a workflow definition
    (shape of the workflow, states, events it can handle, etc)
    """
    code: str  # Mandatory, unique code for the workflow
    name: Optional[str] = None
    description: Optional[str] = None
    initial_state: Optional[Union[StateDefinition, str]] = None
    states: Optional[list[Union[StateDefinition, dict, str]]] = None
    events: Optional[list[Union[EventConfig, dict, str]]] = None
    categories: Optional[list[Union[WorkflowCategoryDefinition, dict, str]]] = None
    # other workflow configurations:
    # the shape of the workflow ID handle (ie: {email: 'string'})
    handle_schema: Optional[dict] = None
    # if the workflow is enabled or not (critical for scheduled workflows!)
    enabled: Optional[bool] = True
    # the trigger for the workflow (ie: continuous, on-demand, scheduled)
    trigger: WorkflowTrigger = WorkflowTrigger.ON_DEMAND
    # The task queue to where this workflow should be run:
    task_queue: Optional[str] = None
    # Advanced configurations for the workflow:
    config: dict[str, Any] = field(default_factory=dict)

    # Include the new methods for the dynamic workflows!
    # keeps track of the workflow to invoke for this WorkflowDefinition:
    workflow: Optional[Callable] = None  # type: ignore
    args: Any = None
    setup_fn: Optional['SetupFunction'] = None
    # private attributes:
    _services_defn: _ServicesDefn = field(
        default_factory=lambda: _ServicesDefn('', {}),
        init=False
    )
    _services_dict: dict[str, Callable] = field(
        default_factory=dict, init=False)
    _child_workflows_defn: _ChildWorkflowsDefn = field(
        default_factory=lambda: _ChildWorkflowsDefn('', {}),
        init=False
    )
    _child_workflows_dict: dict[str, Callable] = field(
        default_factory=dict, init=False)
    # lol, this is a flag to know if the post init was done
    _post_init_done: bool = field(init=False, default=False)

    def __init__(  # pylint: disable=R0913
        self,
        code: str,
        *,
        name: Optional[str] = None,
        workflow: Optional[Callable] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        trigger: WorkflowTrigger = WorkflowTrigger.ON_DEMAND,
        handle_schema: Optional[dict] = None,
        config: Optional[dict[str, Any]] = None,
        task_queue: Optional[str] = None,
        initial_state: Optional[Union[StateDefinition, str]] = None,
        states: Optional[list[Union[StateDefinition, dict, str]]] = None,
        events: Optional[list[Union[EventConfig, dict, str]]] = None,
        categories: Optional[list[Union[WorkflowCategoryDefinition, dict, str]]] = None,
        services: Optional[Union[dict[str, Callable], list[Callable]]] = None,
        child_workflows: Optional[dict[str, Callable]] = None,
        args: Any = None,
        setup_fn: Optional['SetupFunction'] = None

    ) -> None:
        self.code = code
        self.name = name
        self.workflow = workflow
        self.description = description
        self.enabled = enabled
        self.trigger = trigger
        self.handle_schema = handle_schema or {}  # this must never be None
        self.config = config or {}
        self.config['workerType'] = 'STATIC_PYTHON'  # hard-coded value
        self.initial_state = initial_state
        self.states = states
        self.events = events
        self.categories = categories
        self.args = args
        self.task_queue = task_queue
        self.setup_fn = setup_fn
        self._services_defn = _ServicesDefn('', {})
        self._child_workflows_defn = _ChildWorkflowsDefn('', {})
        # validations
        if workflow and not hasattr(self.workflow, "__is_workflow__"):
            raise ValueError(
                "The workflow parameter must be a valid workflow callable " +
                "(decorated with @workflow)")
        # Initialize the services and child workflows
        # standarize the defn.services shape into a dictionary:
        services = services or {}
        if isinstance(services, list):
            self._services_dict = {
                service.__service_name__: create_copy_func(service)
                for service in services}
        elif isinstance(services, dict):
            self._services_dict = {
                service_key: create_copy_func(service)
                for service_key, service in services.items()
            }
        else:
            raise ValueError("services must be a dict or a list of callables")
        # standarize the defn.child_workflows shape into a dictionary:
        self._child_workflows_dict = {
            workflow_key: create_copy_func(child_workflow)
            for workflow_key, child_workflow in child_workflows.items()
        } if child_workflows else {}

        # if the workflow is dynamic, let's pick the available service
        # keys from the dynamic config, and pick the services from the
        # definition (services_dict) or the default_call of the config:
        if self.workflow and hasattr(self.workflow, "__dynamic_config__"):
            service_configs = self.workflow.__dynamic_config__.services
            self._services_dict = {
                service_cfg.service_key:
                    create_copy_func(self._services_dict.get(
                        service_cfg.service_key, service_cfg.default_call))
                for service_cfg in service_configs
                if service_cfg.service_key in self._services_dict or service_cfg.default_call
            }
            # same for the child workflows:
            child_workflow_configs = self.workflow.__dynamic_config__.child_workflows
            self._child_workflows_dict = {
                workflow_cfg.workflow_key: create_copy_func(
                    self._child_workflows_dict.get(
                        workflow_cfg.workflow_key,
                        workflow_cfg.default_call
                    ))
                for workflow_cfg in child_workflow_configs
                if (workflow_cfg.workflow_key in self._child_workflows_dict
                    or workflow_cfg.default_call)
            }
            # Otherwise, create a clean copy of the workflow only for this definition
            # * This would allow us to define more than 1 dynamic
            self.workflow = create_copy_func(self.workflow)
            self.workflow.__vw_defn__ = self
            self.workflow.__name__ = str(self.code)
            # Let's ensure that the definition contains the services that the dynmic
            # workflow has marked as required
            self.__validate_requirements("services")
            self.__validate_requirements("child_workflows")
            # Update possible services that are not required and that may not be defined here
            not_required_services: dict[str, Callable] = {
                service.service_key: create_copy_func(service.default_call)
                for service in filter(lambda svc: svc.required is False,
                                      self.workflow.__dynamic_config__.services)
                if service.service_key not in self._services_dict and service.default_call
            }
            if not_required_services:
                self._services_dict.update(not_required_services)
                # * TODO: Could be good to add a warning here, to tell the user that we're going to
                # * use the default call for these not mandatory services.

            # Update possible child workflows that are not required and that may not be defined here
            not_required_workflows: dict[str, Callable] = {
                workflow.workflow_key: workflow.default_call
                for workflow in filter(lambda wf: wf.required is False,
                                       self.workflow.__dynamic_config__.child_workflows)
                if workflow.workflow_key not in self._child_workflows_dict
            }
            if not_required_workflows:
                self._child_workflows_dict.update(not_required_workflows)
                # * TODO: Could be good to add a warning here, to tell the user that we're going to
                # * use the default call for these not mandatory child workflows.

        # Namespace all registered services with the workflow code to avoid name clashes
        # This applies to all workflow types, not just dynamic ones
        for service in self._services_dict.values():
            if not service:
                continue  # may be a non-required service without default_call
            self.__update_activity_name(
                service, lambda name: f'{self.code}.{name.split(".")[-1]}')

        # Add the service definition
        # Initialize the ServicesDefn instance after the dataclass is initialized:
        self.services = self._services_dict
        self.child_workflows = self._child_workflows_dict

    def __validate_requirements(self, obj_type: Literal["services", "child_workflows"]) -> None:
        """..."""
        # Get the dynamic config
        dynamic_config = getattr(self.workflow, "__dynamic_config__", None)
        # Get the object to validate
        if obj_type == "services":
            key = "service_key"
            objects_dict = self._services_dict
        else:
            key = "workflow_key"
            objects_dict = self._child_workflows_dict
        # Initialize the validation message
        validation_message: str = f'🌱 TEMPLATE: {self.code}' if hasattr(
            self.workflow, "__dynamic_config__") else f'WORKFLOW: {self.code}'
        validation_message += f' {obj_type} requirement:\n'
        # CASES:
        # required and defined (✅ IMPLEMENTED),
        # not required and defined (✅ IMPLEMENTED),
        # not required and using default (⚠️ DEFAULT IMPLEMENTED),
        # not required and not defined (⚠️ WILL SKIP),
        # required and not defined (❌ NOT IMPLEMENTED)
        # Note: the only way to know if a service is defined is by checking the services_dict
        # AND the default_call of the dynamic_config (must not match the default_call)

        # Get the object to validate
        # If it is `child_workflow`, then we should get the child workflows
        # If it is `services`, then we should get the services
        objects_to_validate = getattr(dynamic_config, obj_type)

        required_and_defined: list[str] = [
            getattr(obj, key) for obj in filter(
                lambda o: o.required is True,
                objects_to_validate
            ) if (
                getattr(obj, key) in objects_dict
                and obj.default_call != objects_dict[getattr(obj, key)]
            )
        ]
        not_required_and_defined: list[str] = []
        for obj in objects_to_validate:
            if obj.required is False:
                obj_key = getattr(obj, key)
                if obj_key in objects_dict:
                    # it's considered "defined" if either:
                    # 1. or the default_call is not defined, but the service is
                    if (not obj.default_call and objects_dict[obj_key]):
                        not_required_and_defined.append(obj_key)
                    # or:
                    # 2. the default_call exists,
                    # but the service function name doesn't exactly match it's name
                    # (so it's another function)
                    elif (obj.default_call
                          and objects_dict[obj_key]):
                        # Check if default_call is a service or workflow
                        if hasattr(obj.default_call, '__is_service__'):
                            # For services, compare service names
                            default_service_name = getattr(
                                obj.default_call, '__service_name__', None)
                            actual_service_name = getattr(
                                objects_dict[obj_key], '__service_name__', None)
                            if default_service_name != actual_service_name:
                                not_required_and_defined.append(obj_key)
                        elif hasattr(obj.default_call, '__is_workflow__'):
                            # For workflows, compare wrapped function names
                            if (obj.default_call.__wrapped__.__name__
                                    != objects_dict[obj_key].__wrapped__.__name__):
                                not_required_and_defined.append(obj_key)
                        else:
                            # Neither service nor workflow
                            raise ValueError(
                                f"Default call for {obj_key} is neither a service nor a workflow"
                            )
        not_required_and_using_default: list[str] = [
            getattr(obj, key) for obj in filter(
                lambda o: o.required is False,
                objects_to_validate
            ) if (
                getattr(obj, key) in objects_dict
                and obj.default_call
                and objects_dict[getattr(obj, key)]
                and obj.default_call.__name__ == objects_dict[getattr(obj, key)].__name__
            )
        ]
        not_required_and_not_defined: list[str] = [
            getattr(obj, key) for obj in filter(
                lambda o: o.required is False,
                objects_to_validate
            ) if (
                getattr(obj, key) not in objects_dict
            )
        ]
        required_and_not_defined: list[str] = [
            getattr(obj, key) for obj in filter(
                lambda o: o.required is True,
                objects_to_validate
            ) if (
                getattr(obj, key) not in objects_dict
            )
        ]
        # log all cases in order in the message:
        for case, case_set, case_name, emoji in [
            ('Required', required_and_defined, 'IMPLEMENTED', '✅'),
            ('Not required', not_required_and_defined, 'IMPLEMENTED', '✅'),
            ('Not required', not_required_and_using_default, 'USING DEFAULT', '⚠️ '),
            ('Not required', not_required_and_not_defined, 'WILL SKIP', '⚠️ '),
            ('Required', required_and_not_defined, 'NOT IMPLEMENTED', '❌')
        ]:
            # each message like: "✅ service_n (required): IMPLEMENTED"
            for workflow_key in case_set:
                validation_message += f"\t{emoji} {workflow_key} ({case}): {case_name}\n"

        if len(required_and_not_defined) > 0:
            log(LogLevel.ERROR, validation_message)
            raise RuntimeError(
                f"The dynamic workflow '{self.code}' requires the {key} " +
                f"{list(required_and_not_defined)}, but they were not included in the definition."
            )
        # always log, it's in debug mode anyways
        # if we only wanna report warnings, wrap in an if:
        # if len(not_required_and_not_defined) > 0 or len(not_required_and_using_default) > 0:
        log(LogLevel.DEBUG, validation_message)

    def __update_activity_name(self, activity: Callable, updater: Callable[[str], str]) -> None:
        """Given an activity, update its name with a prefix to avoid duplicates.

        Args:
            activity (Callable): The activity to update.
            updater (Callable[[str], str]): The function to update the name.
        """
        # temporal reference to the activity (service.__temporal_activity_definition.name):
        activity_defn = getattr(
            activity, "__temporal_activity_definition", None)
        if not activity_defn:
            service_name = getattr(
                activity, "__service_name__", activity.__name__)
            raise ValueError(
                f"Activity {service_name} has no definition" +
                "(did you forget to add the @service decorator?)")
        object.__setattr__(activity_defn, "name", updater(activity_defn.name))
        # Keep original __name__ for pickling but update __service_name__
        service_name = getattr(activity, "__service_name__", activity.__name__)
        object.__setattr__(activity, "__service_name__", updater(service_name))

    # Define the properties
    @property
    def services(self) -> _ServicesDefn:
        """Property to access the services."""
        return self._services_defn

    @services.setter
    def services(self, value: dict[str, Callable]) -> None:
        """Setter for the services."""
        self._services_dict = value
        self._services_defn = _ServicesDefn(
            _defn_code=self.code, services=self._services_dict)

    @property
    def child_workflows(self) -> _ChildWorkflowsDefn:
        """Property to access the child workflows."""
        return self._child_workflows_defn

    @child_workflows.setter
    def child_workflows(self, value: dict[str, Callable]) -> None:
        """Setter for the child workflows."""
        self._child_workflows_dict = value
        self._child_workflows_defn = _ChildWorkflowsDefn(
            _defn_code=self.code, workflows=self._child_workflows_dict)
