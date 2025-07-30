"""
This module include all the valiotworkflows classes related.

Classes:
    workflowObject: Include a base class that allow us to serialize/deserialize
        complex types from one State to another
    WorkflowHandler: Include a handler for the Workflow
        running execution, that allow us to execute services
        in a single-execution or in parallel execution
    WorkflowWorker: Include the worker that the projects can use
        to interact with the Workflows API developed.

Decorators:
    workflow: This decorator allow us to initialize a function
        as a workflow to be used in the WorkflowWorker.
"""
from .workflow_object import workflowObject
from .workflow_handler import WorkflowHandler
from .workflow_worker import WorkflowWorker, GqlSyncMode
from .decorator.workflow_decorator import (
    workflow, TemplateDefinition, TemplateServiceConfig, TemplateChildWorkflowConfig
)
from .workflow_setup import SetupResult
from .decorator.workflow_definition import (
    WorkflowDefinition,
    WorkflowTrigger,
    ScheduleOverlapPolicy,
    WorkflowCategoryDefinition
)
from .decorator.state_definition import StateDefinition
from .decorator.category_definition import WorkflowCategoryDefinition
