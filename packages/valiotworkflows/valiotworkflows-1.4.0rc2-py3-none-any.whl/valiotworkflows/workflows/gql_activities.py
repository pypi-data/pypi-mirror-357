"""
Implementation of Temporal activities using GraphQL
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, Any
import json
from datetime import datetime, timedelta
# External dependencies
from temporalio import activity as temporalio_activity
import pytz
import pydash as _py
from pygqlc import GraphQLClient

from valiotworkflows.execution_mode import ServiceExecutionMode
from valiotworkflows.workflows.decorator.workflow_definition import WorkflowDefinition, WorkflowCategoryDefinition
from valiotworkflows.workflows.events.workflow_event import EventConfig

from ..validations import QueryException
from .decorator.utils import standardize_categories, standardize_events, standardize_states

from .mutations import (
    # queries
    GET_WORKFLOW_CONFIG,
    GET_WORKFLOW_CONFIGS,
    GET_TASK_QUEUES,
    WORKFLOW_EVENTS,
    # config mutations
    UPSERT_BULK_TASK_QUEUES,
    UPSERT_BULK_WORKFLOW_EVENT_CATALOGS,
    UPSERT_BULK_WORKFLOWS,
    # runtime mutations
    CREATE_WORKFLOW_RUN,
    FINISH_WORKFLOW_RUN,
    CREATE_CHILD_WORKFLOW_RUN,
    ATTACH_WORKFLOW_RUN_TO_INIT_EVENT,
    UPSERT_STATE_RUN,
    CREATE_STATE_RUN_WITH_SERVICE,
    CREATE_STATE_RUN_WITH_WORKFLOW_RUN_UPDATE,
    CREATE_SERVICE_RUN,
    FINISH_STATE_RUN,
    FINISH_SERVICE_RUN,
    UPDATE_CONTEXT,
    UPDATE_WORKFLOW_RUN_EVENT,
    CREATE_WORKFLOW_RUN_EVENT,
    UPSERT_BULK_WORKFLOW_CATEGORIES,
    UPSERT_BULK_WORKFLOW_WORKFLOW_CATEGORIES,
    UPSERT_SERVICE_RUN_TO_STATE_RUN,
    UPDATE_WORKFLOW_LAST_RUN_AT,
    TASK_QUEUE_WORKER_HEARTBEAT,
)

# Mutation to update task queue's lastListenedAt
UPDATE_TASK_QUEUE_LAST_LISTENED_AT = """
mutation taskQueueHeartbeat(
  $taskQueue: String!
) {
  upsertTaskQueue(
    findBy: {
      code: $taskQueue
    }
    taskQueue: {
      lastListenedAt: "now()"
    }
  ){
    successful
    messages {field message}
    result{
      id
      lastListenedAt
    }
  }
}
"""

env_task_queue = os.environ.get('TEMPORAL_TASK_QUEUE')
# type checker was complaining about the type of the list[str], not sure why
BASE_WORKFLOW_EVENTS: list[EventConfig | dict | str] = [
    'INIT', 'TIMER', 'TIMEOUT', 'ON_INVOCATION_DONE', 'INIT_PARALLEL', 'ON_PARALLEL_DONE']


class GqlActivities:
    """A class to handle GraphQL activities related to workflows.
    Attributes:
        DEFAULT_ACTIVITY_OPTIONS (dict): Default options for activities.
        DEFAULT_LOCAL_ACTIVITY_OPTIONS (dict): Default options for local activities.
        DEFAULT_WFS_ACTIVITY_OPTIONS (dict): Default options for workflow activities.

    Methods:
        get_activities:
            Returns a list of available activity methods.
        create_workflow_run:
            Creates a new workflow run.
        finish_workflow_run:
            Finishes a workflow run.
        create_child_workflow_run:
            Creates a child workflow run.
        attach_workflow_run_to_event:
            Attaches a workflow run to an event.
        upsert_state_run:
            Upserts a state run.
        create_state_run_with_service:
            Creates a state run with a service.
        create_state_run_with_workflow_run_update:
            Creates a state run with a workflow run update.
        create_service_run:
            Creates a service run.
        finish_state_run:
            Finishes a state run.
        finish_service_run:
            Finishes a service run.
        update_workflow_context:
            Updates the context of a workflow run.
        update_workflow_run_event:
            Updates a workflow run event.
        get_workflow_config:
            Retrieves the configuration of a workflow.
        update_workflow_last_run_at:
            Updates the lastRunAt timestamp for a workflow in GraphQL.
        heartbeat_task_queue_worker:
            Sends a heartbeat for a task queue worker to the GraphQL API.
    """
    DEFAULT_ACTIVITY_OPTIONS: dict = {
        'heartbeat_timeout': timedelta(seconds=30),
        'start_to_close_timeout': timedelta(minutes=5)
    }

    DEFAULT_LOCAL_ACTIVITY_OPTIONS: dict = {
        'start_to_close_timeout': timedelta(minutes=5)
    }

    DEFAULT_WFS_ACTIVITY_OPTIONS: dict = {
        "task_queue": os.environ.get('TEMPORAL_ACTIVITIES_TASK_QUEUE', "activities-task-queue")
    }

    def __init__(self, gql_client: GraphQLClient):
        self._gql = gql_client
        self._executor = ThreadPoolExecutor()
        self._loop = asyncio.get_running_loop()

    def get_activities(self) -> list:
        """Returns a list of available activity methods."""
        return [
            self.get_workflow_config,
            self.create_workflow_run,
            self.finish_workflow_run,
            self.create_child_workflow_run,
            self.attach_workflow_run_to_event,
            self.upsert_state_run,
            self.create_state_run_with_service,
            self.create_state_run_with_workflow_run_update,
            self.create_service_run,
            self.finish_state_run,
            self.finish_service_run,
            self.update_workflow_context,
            self.update_workflow_run_event,
            self.create_workflow_run_event,
            self.upsert_service_run,
            self.update_workflow_last_run_at,
            self.heartbeat_task_queue_worker,
        ]

    # ! gql methods -------------------------------------------------------
    @temporalio_activity.defn
    async def create_workflow_run(
        self,
        workflow_code: str,
        raw_handle: Optional[dict[str, Any]] = None,
        task_queue: Optional[str] = None,
        parent_workflow_run_id: Optional[str | int] = None,
        parent_state_run_id: Optional[str | int] = None
    ) -> dict:
        """Creates a new workflow run on the GraphQL API.

        Args:
            workflow_code: The code of the workflow to create a run for
            raw_handle: The raw handle for the workflow instance
            task_queue: The task queue the workflow runs on
            parent_workflow_run_id: Optional ID of the parent workflow run for child workflows
            parent_state_run_id: Optional ID of the parent state run for child workflows

        Returns:
            dict: The created workflow run
        """
        variables = {
            'workflowCode': workflow_code,
            'context': '{}',
            'rawHandle': json.dumps(raw_handle or {}),
            'startedAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            'taskQueue': task_queue,
        }

        # Add parent workflow run ID if provided
        if parent_workflow_run_id is not None:
            variables['parentWorkflowRunId'] = parent_workflow_run_id

        # Add parent state run ID if provided
        if parent_state_run_id is not None:
            variables['parentStateRunId'] = parent_state_run_id

        return await self._mutate_and_validate(
            mutation=CREATE_WORKFLOW_RUN,
            variables=variables,
        )

    @temporalio_activity.defn
    async def finish_workflow_run(self, workflow_run_id: int | str) -> dict:
        """Finishes a workflow run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=FINISH_WORKFLOW_RUN,
            variables={
                'workflowRunId': workflow_run_id,
                'finishedAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            },
        )

    @temporalio_activity.defn
    async def create_child_workflow_run(  # pylint: disable=R0913
        self,
        workflow_code: str,
        parent: dict[str, Any],
        raw_handle: Optional[dict[str, Any]] = None,
        initial_context: Optional[dict[str, Any]] = None,
        task_queue: Optional[str] = None
    ) -> dict:
        """Creates a child workflow run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=CREATE_CHILD_WORKFLOW_RUN,
            variables={
                'workflowCode': workflow_code,
                'context': json.dumps(initial_context or {}),
                'rawHandle': json.dumps(raw_handle or {}),
                'parentStateRunId': parent['stateRunId'],
                'parentWorkflowRunId': parent['workflowRunId'],
                'startedAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
                'taskQueue': task_queue,
            },
        )

    @temporalio_activity.defn
    async def attach_workflow_run_to_event(
        self,
        workflow_run_id: int | str,
        init_event_id: int | str
    ) -> dict:
        """Attaches a workflow run to an event on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=ATTACH_WORKFLOW_RUN_TO_INIT_EVENT,
            variables={
                'eventId': init_event_id,
                'workflowRunId': workflow_run_id,
                'acknowledge': json.dumps({'successful': True}),
            },
        )

    @temporalio_activity.defn
    async def upsert_state_run(self, workflow_run_id: int | str, state_id: int | str) -> dict:
        """Upserts a state run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=UPSERT_STATE_RUN,
            variables={
                'stateId': state_id,
                'workflowRunId': workflow_run_id,
                'enteredAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            },
        )

    @temporalio_activity.defn
    async def create_state_run_with_service(
        self,
        workflow_run_id: int | str,
        state_id: str | int,
        service_id: str | int,
        task_queue: Optional[str] = None
    ) -> dict:
        """Creates a state run with a service on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=CREATE_STATE_RUN_WITH_SERVICE,
            variables={
                'stateId': state_id,
                'workflowRunId': workflow_run_id,
                'enteredAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
                'createServiceRun': {
                    'serviceId': service_id,
                    'status': 'RUNNING',
                    'progress': 0,
                    'taskQueueCode': task_queue,
                },
            },
        )

    @temporalio_activity.defn
    async def create_state_run_with_workflow_run_update(
        self,
        workflow_run_id: int | str,
        state_id: int | str
    ) -> dict:
        """Creates a state run with a workflow run update on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=CREATE_STATE_RUN_WITH_WORKFLOW_RUN_UPDATE,
            variables={
                'stateId': state_id,
                'workflowRunId': workflow_run_id,
                'enteredAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            },
        )

    @temporalio_activity.defn
    async def create_service_run(
        self,
        state_run_id: int | str,
        service_id: int | str,
        task_queue: Optional[str] = None
    ) -> dict:
        """Creates a service run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=CREATE_SERVICE_RUN,
            variables={
                'serviceId': service_id,
                'stateRunId': state_run_id,
                'taskQueue': task_queue,
            },
        )

    @temporalio_activity.defn
    async def finish_state_run(
        self,
        workflow_run_id: int | str,
        state_id: int | str
    ) -> dict:
        """Finishes a state run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=FINISH_STATE_RUN,
            variables={
                'workflowRunId': workflow_run_id,
                'fromStateId': state_id,
                'leftAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            },
        )

    @temporalio_activity.defn
    async def finish_service_run(self, service_run_id: int | str) -> dict:
        """Finishes a service run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=FINISH_SERVICE_RUN,
            variables={
                'serviceRunId': service_run_id,
                'endAt': datetime.now(pytz.utc).isoformat(timespec='seconds'),
            },
        )

    @temporalio_activity.defn
    async def update_workflow_context(
        self,
        workflow_run_id: int | str,
        context: dict[str, Any]
    ) -> dict:
        """Updates the context of a workflow run on the GraphQL API."""
        return await self._mutate_and_validate(
            mutation=UPDATE_CONTEXT,
            variables={
                'workflowRunId': workflow_run_id,
                'context': json.dumps(context),
            },
        )

    @temporalio_activity.defn
    async def update_workflow_run_event(
        self,
        event_id: int | str,
        workflow_run_id: Optional[int | str] = None,
        is_successful: bool = True,
        error_messages: Optional[list[dict[str, str]]] = None,
    ) -> dict:
        """Updates a workflow run event with workflow run ID and response on the GraphQL API."""
        response = {
            "successful": is_successful,
            "messages": error_messages or []
        }

        variables = {
            "id": event_id,
            "response": json.dumps(response),
        }

        # Only include workflowRunId in variables if it's not None and not 0
        if workflow_run_id is not None and workflow_run_id != 0:
            variables["workflowRunId"] = workflow_run_id

        return await self._mutate_and_validate(
            mutation=UPDATE_WORKFLOW_RUN_EVENT,
            variables=variables,
        )

    @temporalio_activity.defn
    async def create_workflow_run_event(
        self,
        workflow_run_id: int | str,
        event_code: str,
        payload: dict[str, Any],
        emitter_token_id: Optional[int | str] = None,
    ) -> dict:
        """Creates a workflow run event on the GraphQL API.

        Args:
            workflow_run_id (int | str): The ID of the workflow run to create the event for
            event_code (str): The code of the event to create
            payload (dict[str, Any]): The payload of the event
            emitter_token_id (Optional[int | str]): The ID of the token that emitted the event

        Returns:
            dict: The created workflow run event
        """
        variables = {
            "workflowRunId": workflow_run_id,
            "eventCode": event_code,
            "payload": json.dumps(payload),
            "response": json.dumps({"successful": True, "messages": []}),
        }

        # Only include emitterTokenId if it's provided
        if emitter_token_id is not None:
            variables["emitterTokenId"] = emitter_token_id

        return await self._mutate_and_validate(
            mutation=CREATE_WORKFLOW_RUN_EVENT,
            variables=variables,
        )

    @temporalio_activity.defn
    async def get_workflow_config(self, workflow_code: str) -> dict:
        """Retrieves the configuration of a workflow.

        Raises:
            RuntimeError: If there is an error in the query.
        """
        config_future = self._get_workflow_config(workflow_code)
        task_queues_future = self._get_task_queues()
        events_future = self._get_workflow_events(workflow_code)

        config_result, task_queues_result, events_result = await asyncio.gather(
            config_future, task_queues_future, events_future)
        workflow_config, config_errors = config_result
        task_queues, task_queues_errors = task_queues_result
        workflow_events, events_errors = events_result

        if config_errors:
            raise RuntimeError(config_errors)
        if task_queues_errors:
            raise RuntimeError(task_queues_errors)
        if events_errors:
            raise RuntimeError(events_errors)

        return stitch_task_queues_to_workflow(
            {**workflow_config, 'events': workflow_events},  # type: ignore
            task_queues  # type: ignore
        )

    @temporalio_activity.defn
    async def get_workflow_configs(self, workflow_codes: list[str]) -> list[dict[str, Any]]:
        """Retrieves the configuration of multiple workflows.

        Raises:
            RuntimeError: If there is an error in the query.
        """
        configs_result = await self._get_workflow_configs(workflow_codes)
        workflow_configs, errors = configs_result

        if errors:
            raise RuntimeError(errors)
        if not workflow_configs:
            raise RuntimeError(
                'Empty response from GraphQL query for workflow configs')
        assert isinstance(workflow_configs,
                          list), 'Expected a list of workflow configs'
        assert all(isinstance(config, dict)
                   for config in workflow_configs), 'Expected workflow configs to be dicts'
        return workflow_configs

    @temporalio_activity.defn
    async def upsert_workflow_configs(self, workflow_defns: list[WorkflowDefinition]) -> None:
        """Upserts the configuration of multiple workflows.

        Raises:
            RuntimeError: If there is an error in the query.
        """
        # ! 1. upsert global task queues
        await self._upsert_task_queues(workflow_defns)
        # ! 2. upsert global WorkflowEvents
        await self._upsert_workflow_event_catalogs(workflow_defns)
        # ! 3. upsert global WorkflowCategories
        await self._upsert_workflow_categories(workflow_defns)
        # ! 4. upsert workflow configs
        bulk_workflow_upserts_result = await self._upsert_workflow_configs(workflow_defns)
        upserted_workflows: list[dict[str, Any]] = bulk_workflow_upserts_result.get(
            'workflows', [])
        # ! 5. update workflow configs which had initialState set up
        # (cannot be done in a single operation)
        await self._upsert_workflow_initial_states(
            workflow_defns,
            upserted_workflows
        )
        # ! 6. connect workflows with categories (many-to-many relationships)
        await self._upsert_workflow_workflow_categories(workflow_defns)

    @temporalio_activity.defn
    async def upsert_service_run(
        self,
        state_run_id: int | str,
        service_id: int | str,
        task_queue: Optional[str] = None
    ) -> dict:
        """Upserts a service run to a state run on the GraphQL API.

        Using upsert is preferred over create as it is idempotent and handles race conditions better.

        Args:
            state_run_id: The ID of the state run to attach the service to
            service_id: The ID of the service to run
            task_queue: Optional task queue to run the service on

        Returns:
            dict: The upserted service run details
        """
        return await self._mutate_and_validate(
            mutation=UPSERT_SERVICE_RUN_TO_STATE_RUN,
            variables={
                'stateRunId': state_run_id,
                'serviceId': service_id,
                'taskQueue': task_queue,
            },
        )

    @temporalio_activity.defn
    async def update_workflow_last_run_at(self, workflow_code: str) -> dict:
        """Updates the lastRunAt timestamp to the current time.

        Args:
            workflow_code: The code of the workflow to update

        Returns:
            dict: The response from the GraphQL API
        """
        return await self._mutate_and_validate(
            mutation=UPDATE_WORKFLOW_LAST_RUN_AT,
            variables={'workflowCode': workflow_code},
        )

    @temporalio_activity.defn
    async def heartbeat_task_queue_worker(
        self,
        session_guid: str,
        task_queue: str,
        worker_version: str | None = None,
    ) -> dict:
        """Sends a heartbeat for a task queue worker to the GraphQL API.

        Args:
            session_guid: Unique identifier for the worker session
            task_queue: The task queue the worker is running on
            worker_version: Optional version of the worker

        Returns:
            dict: The result of the mutation
        """
        # Prepare variables for the worker heartbeat mutation
        heartbeat_variables = {
            'sessionGuid': session_guid,
            'taskQueue': task_queue,
        }

        # Only include worker_version if it's provided
        if worker_version is not None:
            heartbeat_variables['workerVersion'] = worker_version

        # Prepare variables for updating the task queue's lastListenedAt
        last_listened_variables = {
            'taskQueue': task_queue,
        }

        # Execute both mutations in parallel
        worker_heartbeat_future = self._mutate_and_validate(
            mutation=TASK_QUEUE_WORKER_HEARTBEAT,
            variables=heartbeat_variables,
        )

        update_last_listened_future = self._mutate_and_validate(
            mutation=UPDATE_TASK_QUEUE_LAST_LISTENED_AT,
            variables=last_listened_variables,
        )

        # Wait for both mutations to complete
        worker_result, _last_listened_result = await asyncio.gather(
            worker_heartbeat_future,
            update_last_listened_future
        )

        # Return the worker heartbeat result (maintaining backward compatibility)
        return worker_result

    # internal utils

    async def _get_workflow_config(self, workflow_code: str):
        return await self._gql.async_query(
            GET_WORKFLOW_CONFIG,
            variables={'workflowCode': workflow_code},
        )

    async def _get_task_queues(self):
        return await self._gql.async_query(GET_TASK_QUEUES)

    async def _get_workflow_events(self, workflow_code: str):
        return await self._gql.async_query(
            WORKFLOW_EVENTS,
            variables={'workflowCode': workflow_code},
        )

    async def _get_workflow_configs(self, workflow_codes: list[str]):
        return await self._gql.async_query(
            GET_WORKFLOW_CONFIGS,
            variables={'workflowCodes': workflow_codes},
        )

    async def _upsert_task_queues(self, workflow_defns: list[WorkflowDefinition]):
        '''Upsert task queues into the GraphQL API
        '''
        # both default task queues and the ones required for the workflows and services
        task_queues: list[str] = get_task_queues_from_workflow_defns(
            workflow_defns)
        task_queues_params = get_gql_task_queues_params(task_queues)
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_TASK_QUEUES,
            variables={'taskQueues': task_queues_params},
        )

    async def _upsert_workflow_event_catalogs(self, workflow_defns: list[WorkflowDefinition]):
        '''Upsert workflow event catalogs into the GraphQL API
        '''
        event_catalogs_to_upload = get_global_workflow_events(
            workflow_defns)
        workflow_event_catalogs_params = get_gql_workflow_event_catalogs_params(
            event_catalogs_to_upload)
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_WORKFLOW_EVENT_CATALOGS,
            variables={'workflowEventCatalogs': workflow_event_catalogs_params},
        )

    async def _upsert_workflow_categories(self, workflow_defns: list[WorkflowDefinition]):
        '''Upsert workflow categories into the GraphQL API
        '''
        workflow_categories_params = get_gql_workflow_categories_params(
            get_global_workflow_categories(workflow_defns))
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_WORKFLOW_CATEGORIES,
            variables={'workflowCategories': workflow_categories_params},
        )

    async def _upsert_workflow_workflow_categories(self, workflow_defns: list[WorkflowDefinition]):
        '''Upsert workflow-workflow category relationships into the GraphQL API
        '''
        workflow_workflow_categories_params = get_gql_workflow_workflow_categories_params(
            workflow_defns)
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_WORKFLOW_WORKFLOW_CATEGORIES,
            variables={
                'workflowWorkflowCategories': workflow_workflow_categories_params},
        )

    async def _upsert_workflow_configs(self, workflow_defns: list[WorkflowDefinition]):
        '''Upsert workflow configs into the GraphQL API
        '''
        workflow_configs_params = get_gql_workflow_configs_params(
            workflow_defns)
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_WORKFLOWS,
            variables={'workflows': workflow_configs_params},
        )

    async def _upsert_workflow_initial_states(
        self,
        workflow_defns: list[WorkflowDefinition],
        upserted_workflows: list[dict[str, Any]]
    ):
        '''Upsert workflow initial states into each corresponding workflow config
        '''
        workflow_initial_states_params = get_gql_workflow_initial_state_params(
            workflow_defns, upserted_workflows)
        return await self._mutate_and_validate(
            mutation=UPSERT_BULK_WORKFLOWS,
            variables={'workflows': workflow_initial_states_params},
        )

    # ! end gql methods ---------------------------------------------------

    # ! internal methods --------------------------------------------------

    async def _mutate_and_validate(self, mutation: str, variables: dict[str, Any]) -> dict[str, Any]:
        response, errors = await self._gql.async_mutate(mutation, variables=variables)
        self._validate_gql_mutation_response(response, errors)  # type: ignore
        return response.get('result', None)  # type: ignore

    def _validate_gql_mutation_response(
        self,
        response: dict[str, Any] | None,
        errors: list[dict[str, Any]] | None
    ) -> None:
        # TODO: raise custom exceptions for different error types
        if errors:
            raise QueryException(errors[0])
        if not response:
            raise QueryException('Empty response from GraphQL mutation')
        if not response.get('successful', False):
            if not response.get('messages', []):
                raise QueryException(
                    'The gql mutation failed without error messages')
            raise QueryException(response.get('messages', [])[0]['message'])

    # ! end internal methods ----------------------------------------------

# ! other utils:


def stitch_task_queues_to_workflow(workflow: dict, task_queues: list) -> dict:
    '''
    Stitch task queues to workflow object,
    useful because of valiot-app complexity limitations
    '''
    return {
        **workflow,
        "events": workflow.get("events", []),
        # stitch missing workflow.taskQueue (query too complex to handle it)
        "taskQueue": _py.find(task_queues, lambda tq: tq['id'] == workflow['taskQueueId']),
        "services": [
            {
                **service,
                # stitch missing workflow.services[n].taskQueue (query too complex to handle it)
                "taskQueue": _py.find(
                    task_queues,
                    lambda tq: tq['id'] == service['taskQueueId']  # pylint: disable=W0640
                ),
            }
            for service in workflow.get("services", [])
        ],
        "states": [
            {
                **state,
                "invoke": state.get("invoke")
                and {
                    **state["invoke"],
                    # stitch missing workflow.states[n].invoke.taskQueue
                    # (query too complex to handle it)
                    # "taskQueue": next(
                    #     (
                    #         task_queue
                    #         for task_queue in task_queues
                    #         if task_queue["id"] == state["invoke"].get("taskQueueId")
                    #     ),
                    #     None,
                    # ),
                    "taskQueue": _py.find(
                        task_queues,
                        lambda tq: tq['id'] == _py.get(
                            state, 'invoke.taskQueueId'  # pylint: disable=W0640
                        )
                    ),
                    "service": _py.get(state, "invoke.service")
                    and {
                        **_py.get(state, "invoke.service"),
                        # stitch missing workflow.states[n].invoke.service.taskQueue
                        # (query too complex to handle it)
                        "taskQueue": _py.find(
                            task_queues,
                            lambda tq: tq['id'] == _py.get(
                                state, 'invoke.service.taskQueueId'  # pylint: disable=W0640
                            )
                        ),
                    },
                },
            }
            for state in workflow.get("states", [])
        ],
    }


def get_task_queues_from_workflow_defns(workflow_defns: list[WorkflowDefinition]) -> list[str]:
    '''
    Extracts task queues from workflow definitions
    '''
    task_queues: list[str] = [
        'default-valiotworkflows-task-queue',
        'default-cpu-bound-task-queue',
        'workflows-task-queue',
        'activities-task-queue',
    ]
    for wf_defn in workflow_defns:
        if wf_defn.task_queue and wf_defn.task_queue not in task_queues:
            task_queues.append(wf_defn.task_queue)
        # same for services:
        for service in wf_defn.services:
            if not service:
                continue
            if service.__task_queue__ and service.__task_queue__ not in task_queues:
                task_queues.append(service.__task_queue__)
        # same for child workflows:
        for child_wf in wf_defn.child_workflows:
            if not child_wf or not child_wf.__vw_defn__:
                continue
            child_wf_defn: WorkflowDefinition = child_wf.__vw_defn__
            if child_wf_defn.task_queue and child_wf_defn.task_queue not in task_queues:
                task_queues.append(child_wf_defn.task_queue)
    return task_queues


def get_task_queue_from_workflow_defn(workflow_defn: WorkflowDefinition) -> str:
    '''Gets the task queue from a workflow definition based on the chain of defaults
    '''
    if workflow_defn.task_queue:
        return workflow_defn.task_queue
    elif workflow_defn.workflow and workflow_defn.workflow.__task_queue__:
        return workflow_defn.workflow.__task_queue__
    elif env_task_queue:
        return env_task_queue
    else:
        return 'default-valiotworkflows-task-queue'


def get_task_queue_from_service(service: Callable) -> str:
    '''Gets the task queue from a service based on the chain of defaults
    '''
    if service.__task_queue__:
        return service.__task_queue__
    elif env_task_queue:
        return env_task_queue
    elif service.__execution_mode__ == ServiceExecutionMode.CPU_BOUND:
        return 'default-cpu-bound-task-queue'
    else:
        return 'default-valiotworkflows-task-queue'


def get_global_workflow_events(workflow_defns: list[WorkflowDefinition]) -> list[EventConfig]:
    '''
    Extracts global workflow events from workflow definitions
    '''
    global_workflow_events = standardize_events(BASE_WORKFLOW_EVENTS)

    for wf_defn in workflow_defns:
        wf_defn_events: list[Any] = wf_defn.events or []
        std_wf_defn_events: list[EventConfig] = standardize_events(
            wf_defn_events)

        for wf_event in std_wf_defn_events:
            if not any(wf_event.code == event.code for event in global_workflow_events):
                global_workflow_events.append(wf_event)

        # and for child workflows:
        for child_wf in wf_defn.child_workflows:
            if not child_wf or not child_wf.__vw_defn__:
                continue
            child_wf_defn: WorkflowDefinition = child_wf.__vw_defn__
            child_wf_defn_events: list[Any] = child_wf_defn.events or []
            std_child_wf_defn_events: list[EventConfig] = standardize_events(
                child_wf_defn_events)
            for child_wf_event in std_child_wf_defn_events:
                if not any(child_wf_event.code == event.code for event in global_workflow_events):
                    global_workflow_events.append(child_wf_event)

    return global_workflow_events


def get_global_workflow_categories(
        workflow_defns: list[WorkflowDefinition]
) -> list[WorkflowCategoryDefinition]:
    '''
    Extracts global workflow categories from workflow definitions
    '''
    global_workflow_categories: list[WorkflowCategoryDefinition] = []
    category_codes: set[str] = set()  # Track unique category codes

    for wf_defn in workflow_defns:
        wf_defn_categories: list[Any] = wf_defn.categories or []
        std_wf_defn_categories: list[WorkflowCategoryDefinition] = standardize_categories(
            wf_defn_categories)

        for wf_category in std_wf_defn_categories:
            if wf_category.code not in category_codes:
                global_workflow_categories.append(wf_category)
                category_codes.add(wf_category.code)

        # and for child workflows:
        for child_wf in wf_defn.child_workflows:
            if not child_wf or not child_wf.__vw_defn__:
                continue
            child_wf_defn: WorkflowDefinition = child_wf.__vw_defn__
            child_wf_defn_categories: list[Any] = child_wf_defn.categories or [
            ]
            std_child_wf_defn_categories: list[WorkflowCategoryDefinition] = standardize_categories(
                child_wf_defn_categories)
            for child_wf_category in std_child_wf_defn_categories:
                if child_wf_category.code not in category_codes:
                    global_workflow_categories.append(child_wf_category)
                    category_codes.add(child_wf_category.code)

    return global_workflow_categories


def get_gql_task_queues_params(task_queues: list[str]) -> list[dict[str, Any]]:
    '''
    Returns a list of task queues parameters for GraphQL bulk mutation
    '''
    return [
        {
            "findBy": {"code": tk},
            "taskQueue": {
                "name": tk,
                "queueKind": "MIXED"
            }
        }
        for tk in task_queues
    ]


def get_gql_workflow_event_catalogs_params(event_cfgs: list[EventConfig]) -> list[dict[str, Any]]:
    '''
    Returns a list of workflow event catalogs parameters for GraphQL bulk mutation
    '''
    return [
        {
            "findBy": {"code": event.code},
            "workflowEventCatalog": {
                "name": event.code
            }
        }
        for event in event_cfgs
    ]


def get_gql_workflow_categories_params(
    category_cfgs: list[WorkflowCategoryDefinition]
) -> list[dict[str, dict[str, Any]]]:
    '''
    Returns a list of workflow categories parameters for GraphQL bulk mutation
    '''
    return [
        {
            "findBy": {"code": category.code},
            "workflowCategory": {
                "name": category.name,
                "description": category.description or category.name
            }
        }
        for category in category_cfgs
    ]


def get_gql_workflow_workflow_categories_params(
    workflow_defns: list[WorkflowDefinition]
) -> list[dict[str, dict[str, Any]]]:
    '''
    Returns a list of workflow-workflow category relationships for GraphQL bulk mutation
    '''
    result: list[dict[str, dict[str, Any]]] = []

    for wf_defn in workflow_defns:
        if not wf_defn.categories:
            continue

        wf_categories = standardize_categories(wf_defn.categories)
        for category in wf_categories:
            result.append({
                "findBy": {
                    "findByCategory": {"code": category.code},
                    "findByWorkflow": {"code": wf_defn.code}
                }
            })

    return result


def get_gql_workflow_configs_params(workflow_defns: list[WorkflowDefinition]) -> list[dict[str, Any]]:
    '''
    Returns a list of workflow configs parameters for GraphQL bulk mutation
    '''
    return [
        {
            "findBy": {"code": wf_defn.code},
            "workflow": {
                "name": wf_defn.code,
                "description": wf_defn.code,
                "trigger": wf_defn.trigger.value,
                "enabled": wf_defn.enabled,
                "handleSchema": str_dict(wf_defn.handle_schema),
                "taskQueueCode": get_task_queue_from_workflow_defn(wf_defn),
                "config": get_workflow_config_param(wf_defn.config)
            },
            "upsertEvents": [
                {
                    "findBy": {"findByEvent": {"code": event.code}},
                    "workflowEvent": {
                        "payloadSchema": (
                            str_dict(wf_defn.handle_schema)
                            # ensure INIT event has the workflow handle schema
                            # for the workflow router to pass initial event properly:
                            if event.code == 'INIT' and not event.payload_schema
                            else str_dict(event.payload_schema)
                        )
                    }
                }
                for event in standardize_events([*BASE_WORKFLOW_EVENTS, *(wf_defn.events or [])])
            ],
            "upsertServices": [
                {
                    "findBy": {"code": service_name},
                    "workflowService": {
                        "name": service_name,
                        "taskQueueCode": get_task_queue_from_service(service)
                    }
                }
                for service in wf_defn.services
                if service and (service_name := extract_service_name(service))
            ],
            "upsertStates": [
                {
                    "findBy": {"code": state.code},
                    "workflowState": {
                        "nameI18nKey": state.name,
                        "descriptionI18nKey": state.name,
                        "type": "NORMAL"
                    }
                }
                for state in standardize_states(wf_defn.states or [])
            ]
        }
        for wf_defn in workflow_defns
    ]


def get_gql_workflow_initial_state_params(
    workflow_defns: list[WorkflowDefinition],
    upserted_workflows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    '''
    Returns a list of workflow initial states parameters for GraphQL bulk mutation
    '''
    initial_state_params: list[dict[str, Any]] = []
    for wf_defn in workflow_defns:
        if wf_defn.initial_state:
            ini_state = standardize_states([wf_defn.initial_state])[0]
            # find corresponding upserted workflow by code
            upserted_wf = _py.find(
                upserted_workflows,
                lambda uw: uw.get(
                    'code') == wf_defn.code  # pylint: disable=W0640
            )
            if not upserted_wf:
                continue
            # find initialStateId from upserted states by state code:
            ini_state_match = _py.find(
                upserted_wf.get('states', []),
                lambda us: us.get(
                    'code') == ini_state.code  # pylint: disable=W0640
            )
            if not ini_state_match:
                raise RuntimeError(
                    f"Initial state '{ini_state.code}' not found in upserted states for workflow '{wf_defn.code}'")
            initial_state_params.append({
                "findBy": {"code": wf_defn.code},
                "workflow": {
                    "initialStateId": ini_state_match.get('id')
                }
            })
    return initial_state_params


def get_workflow_config_param(config: dict[str, Any]) -> str:
    '''Map a WorkflowConfig to a string representation that can be used by graphQL variables
    '''
    return str_dict(config)


def str_dict(d: Optional[dict | str]) -> str:
    '''ensures a dict or string representation of a dict is a string
    '''
    if d is None:
        return 'null'
    return d if isinstance(d, str) else json.dumps(d)


def extract_service_name(service: Callable) -> str:
    '''Gets the name of a service without the workflow prefix
    before: "WORKFLOW_CODE.SERVICE_NAME"
    after: "SERVICE_NAME"
    '''
    # Get service name from __service_name__ if available, falling back to __name__
    service_name = getattr(service, "__service_name__", service.__name__)
    return service_name.split('.')[-1]
