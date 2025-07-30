"""
Workflow Worker
"""
import os
from enum import Enum
import re
import uuid
import asyncio
import tomllib  # Use tomllib for Python 3.11+
import multiprocessing
import concurrent.futures
from typing import Any, Callable, Optional, Sequence, TypeVar
from datetime import timedelta
from argparse import ArgumentParser
# Temporal imports
from temporalio.worker import Worker, SharedStateManager
from temporalio.client import Client
# other imports
import pydash as _py
from valiotlogging import log, LogLevel

# Local imports
from .gql_activities import GqlActivities
from ..workflows.decorator.workflow_decorator import TemplateDefinition
from ..workflows.decorator.workflow_definition import WorkflowDefinition
from ..workflows.workflow_setup import SetupResult
from ..workflows.temporal_workflow import ValiotPythonWorkflow
from ..validations import validate_gql_connection
from ..config import connect_to_temporal, setup_gql
from ..execution_mode import ServiceExecutionMode
from ..redis import (
    has_async_client_instance,
    get_async_client_instance,
    has_sync_client_instance,
    get_sync_client_instance,
)


class GqlSyncMode(str, Enum):
    '''GraphQL sync modes on Worker startup'''
    SYNC = 'SYNC'  # default, upsert workflows and services
    SKIP = 'SKIP'  # skip validation and modifications


WORKFLOW = TypeVar("WORKFLOW")

gql = setup_gql()
TEMPORAL_TASK_QUEUE: str | None = os.environ.get("TEMPORAL_TASK_QUEUE")
TEMPORAL_CPU_BOUND_TASK_QUEUE: str = os.environ.get(
    "TEMPORAL_CPU_BOUND_TASK_QUEUE", "default-cpu-bound-task-queue"
)


def report_current_workflows(workflows: dict[str, Callable]) -> None:
    """Given the dictionary of workflows, report them in a simple list
    so the user knows what are the available options to execute.
    """
    log(LogLevel.INFO, "Available workflows are:")
    for workflow in workflows:
        log(LogLevel.INFO, f"    - {workflow}")


def report_current_services(services: list[Callable]) -> None:
    """Given the list of services, report them in a simple list
    so the user knows what are the available options to execute.
    """
    has_cpu_bound_services = any(
        getattr(s, "__execution_mode__",
                ServiceExecutionMode.IO_BOUND) == ServiceExecutionMode.CPU_BOUND
        for s in services
    )
    log(LogLevel.INFO, "Available services are:")
    for service in services:
        match service.__service_type__:
            case "WORKFLOWS_STUDIO":
                kind = "WF_STUDIO"
            case "STATIC_WORKFLOW":
                kind = "STATIC_WF"
            case "CUSTOM":
                kind = "CUSTOM"
            case _:
                raise ValueError(
                    f"Unknown service type: {service.__service_type__}")

        # Add execution mode prefix if any service is CPU-bound
        execution_mode = getattr(
            service, "__execution_mode__", ServiceExecutionMode.IO_BOUND)
        execution_mode_emoji = "🧠" if execution_mode == ServiceExecutionMode.CPU_BOUND else "🔀"
        execution_mode_prefix = f"[{execution_mode_emoji} {execution_mode.value.ljust(10)}] "
        mode_prefix = execution_mode_prefix if has_cpu_bound_services else " "

        log(LogLevel.INFO,
            f"    - {mode_prefix}[{kind.ljust(10)}] {service.__service_name__}")


def validate_activities_queue(services: list[Callable]) -> None:
    """Given the list of activities, validate that they have the correct
    queue to run.
    """
    # services that are CPU-bound don't need this validation, as this is for retrocompatibility only:
    wfs_services = [
        service.__service_name__ for service in services
        if service.__service_type__ == "WORKFLOWS_STUDIO"
        and service.__execution_mode__ == ServiceExecutionMode.IO_BOUND
    ]
    if not wfs_services:
        return

    if TEMPORAL_TASK_QUEUE != "activities-task-queue":
        log(LogLevel.WARNING,
            "The services running as a @workflows_studio_service run " +
            "in the 'activities-task-queue' by default.\n" +
            f"(Currently running at '{TEMPORAL_TASK_QUEUE}' task queue).\n" +
            "Please make sure to run this service within a Worker with the correct task queue,\n" +
            "either by setting up a different task queue at the .env, or by configuring" +
            " the `service.taskQueue` at graphql for each service.\n" +
            f"The current services that require this are: {wfs_services}"
            )


class WorkflowWorker:
    """This class provides functionality for setting up workflows and
    activities, connecting to Temporal, and running the Temporal worker.

    Methods:
        set_workflows: Set the workflows for the WorkflowWorker instance.
        set_services: Set the activity services for the WorkflowWorker instance.
        connect: Connect to Temporal and initialize the Temporal worker.
        run: Run the Temporal worker.
        enable_session_heartbeat: Enable session heartbeat for the worker.
        set_version: Set worker version for heartbeat.
        get_version_from_toml: Get version from pyproject.toml file.
        set_max_cpu_workers: Set the maximum number of CPU workers for CPU-bound activities.
    """
    # Group of validities
    _workflows: dict[str, dict[str, Callable]]
    _activities: list[Callable]
    _temporal_worker: Worker
    _temporal_cpu_worker: Optional[Worker] = None
    _gql_sync_mode: GqlSyncMode = GqlSyncMode.SYNC
    _gql_activities: GqlActivities
    # Also, define the agent
    _agent: str
    # Session heartbeat flags and parameters
    _heartbeat_enabled: bool = False
    _worker_version: Optional[str] = None
    _session_guid: str = str(uuid.uuid4())
    # CPU-bound worker settings
    _max_cpu_workers: Optional[int] = None
    # _remote_workflows_config: list[dict[str, Any]] = []

    def __init__(self) -> None:
        self._workflows: dict[str, dict[str, Callable]] = {"*": {}}
        self._activities = []
        # Temporal worker
        self._temporal_worker = None  # type: ignore
        # allow for control of the gql sync mode from env variable:
        environ_gql_sync_mode = os.environ.get(
            "GQL_SYNC_MODE", 'SYNC')
        self._gql_sync_mode = GqlSyncMode(environ_gql_sync_mode)
        # default, will be populated with remote data on `self.validate_gql_workflows()`:
        self._remote_workflows_config: list[dict[str, Any]] = []
        # CPU-bound worker settings
        self._max_cpu_workers = None
        # Also, perform an argument parser to get the agents
        parser = ArgumentParser()
        parser.add_argument(
            "-a", "--agent",
            default="*",
            required=False,
            help="In this execution, decide which agent do you want to run to know" +
            " which workflows you can execute in this session."
        )
        args = parser.parse_args()
        # Get the agent from the args
        self._agent = args.agent
        if self._agent == "*":
            log(LogLevel.WARNING, "Not Agent provided, using the default agent '*'...")
        self._gql_activities = GqlActivities(gql)

    def set_max_cpu_workers(self, count: int) -> None:
        """Set the maximum number of CPU workers for CPU-bound activities.

        Args:
            count (int): The maximum number of workers to use in the process pool
                         for CPU-bound activities.
        """
        if count <= 0:
            raise ValueError("Max CPU workers count must be greater than 0")

        cpu_count = multiprocessing.cpu_count()
        if count > cpu_count:
            log(LogLevel.WARNING,
                f"Requested {count} CPU workers exceeds available CPU count ({cpu_count})")

        self._max_cpu_workers = count
        log(LogLevel.INFO, f"Set max CPU workers to {count}")

    def set_gql_sync_mode(self, mode: GqlSyncMode) -> None:
        '''Set the GraphQL sync mode on Worker startup.

        Args:
            mode (GqlSyncMode): The sync mode to set.
        '''
        self._gql_sync_mode = mode

    def add_workflow_definitions(
        self,
        wf_defns: Sequence[WorkflowDefinition | TemplateDefinition],
        agent: str = '*'
    ) -> None:
        '''Add a list of `WorkflowDefinition`'s to the worker.

        This will automatically pick both `defn.workflow` and
        `defn.services` for each definition provided.
        If TemplateDefinition is passed, it will add each
        `template.services[n].default_call` to the worker.

        Args:
            workflows (list[WorkflowDefinition | TemplateDefinition]):
                A list of Workflow or Template definitions.
            agent (str): The agent to assign these workflows. Defaults to '*' (general agent).
        '''
        if not wf_defns:
            raise ValueError(
                "No workflow definitions provided to add_workflow_definitions.")
        for defn in wf_defns:
            log(LogLevel.DEBUG,
                f"starting workflow {defn.code} registration...")
            if isinstance(defn, WorkflowDefinition):
                if not defn.workflow:
                    raise ValueError(
                        f"Workflow definition {defn.code}" +
                        "has no workflow implementation (`defn.workflow`).")
                # validate workflow registration
                # defn.task_queue is at workflow level, __task_queue__ could be at template level
                workflow_tq = defn.task_queue or defn.workflow.__task_queue__
                should_register_wf = workflow_tq == TEMPORAL_TASK_QUEUE
                if not should_register_wf:
                    log(LogLevel.DEBUG,
                        '\t⚠️  Skipped workflow registration, ' +
                        'because it is not assigned to the current task queue' +
                        f' (expects \'{workflow_tq}\' task_queue).')
                # validate services registration
                # (could register even if workflow is not assigned to the current task queue)
                current_workflow_services: list[Callable[..., Any]] = []
                # could be a list or a dict of services
                # first consolidate all services to a list (could also be a dict)
                _iter_services = defn.services.values() if isinstance(
                    defn.services, dict) else defn.services
                # filter out None values
                _iter_services = [srv for srv in _iter_services if srv]
                # then filter out services not assigned to the current task queue
                for service in _iter_services:
                    if service.__task_queue__ == TEMPORAL_TASK_QUEUE or service.__task_queue__ == TEMPORAL_CPU_BOUND_TASK_QUEUE:
                        current_workflow_services.append(service)
                    else:
                        log(LogLevel.DEBUG,
                            f'\t⚠️  Skipped service `{defn.code}.{service.__service_name__}`' +
                            'registration because it is not assigned to the current task queue.')
                # also register child workflows if any:
                if defn.child_workflows:
                    child_defns: list[WorkflowDefinition] = [
                        child_workflow.__vw_defn__
                        for child_workflow
                        in defn.child_workflows.values()
                    ]
                    # add missing task queue if it was defined at @workflow level
                    # but not at defn level:
                    for child_defn in child_defns:
                        if (
                            not child_defn.task_queue
                            and child_defn.workflow
                            and child_defn.workflow.__task_queue__
                        ):
                            child_defn.task_queue = child_defn.workflow.__task_queue__
                    self.add_workflow_definitions(child_defns, agent=agent)
                # proceed to the actual workflow registration:
                if should_register_wf:
                    if agent not in self._workflows:
                        self._workflows[agent] = {}
                    # add workflows related to each definition:
                    self._workflows[agent].update({defn.code: defn.workflow})
                    self._workflows["*"].update({defn.code: defn.workflow})
                # proceed to actual services registration:
                if current_workflow_services:
                    self.add_services(current_workflow_services)
                if not defn.services:
                    # maybe it uses only general services defined by another template or workflow
                    log(LogLevel.DEBUG,
                        "\t⚠️  Workflow definition has no related `services` declared.")
            elif isinstance(defn, TemplateDefinition):
                current_template_services: list[Callable[..., Any]] = []
                # could be a list or a dict of service configs
                _iter_template_service_configs = defn.services.values() if isinstance(
                    defn.services, dict) else defn.services

                for service_config in _iter_template_service_configs:
                    service = service_config.default_call
                    if not service:
                        continue
                    if service.__task_queue__ == TEMPORAL_TASK_QUEUE or service.__task_queue__ == TEMPORAL_CPU_BOUND_TASK_QUEUE:
                        current_template_services.append(service)
                    else:
                        service_ref = f"{defn.code}.{service.__service_name__}"
                        log(LogLevel.DEBUG,
                            f'⚠️  Skipped service `TEMPLATE:{service_ref}` registration' +
                            'because it is not assigned to the current task queue.')

                if current_template_services:
                    self.add_services(current_template_services)
            else:
                raise ValueError(
                    f"Invalid workflow definition type: {type(defn)}")

    def set_workflows(self, workflows_assignations: dict[str, list[Callable]]) -> None:
        """Set the workflows for the WorkflowWorker instance.

        Args:
            workflows (dict[str, Callable]): A list of workflow functions.

        Raises:
            TypeError: If any of the provided workflows is not of the expected type.
        """
        if not isinstance(workflows_assignations, dict):
            raise TypeError(
                "The provided Workflows must be a dictionary with the agent as a key and a"
                " list of workflows as value. It should be as { AGENT: [WORKFLOWS] }."
            )
        # Iterate over all the workflows to validate them
        for agent, workflows in workflows_assignations.items():
            for workflow in workflows:
                # Now, evaluate the workflow
                if hasattr(workflow, "__is_workflow__") is False:
                    raise TypeError(
                        f"The workflow provided {workflow.__name__} is not a workflow type.\n" +
                        "Hint: Use the ValiotWorkflow decorator `@workflow` in this function."
                    )
                # Iterate if this workflow works for
                if agent not in self._workflows:
                    self._workflows[agent] = {}
                # Use workflow_name if available, fallback to name for compatibility
                workflow_name = getattr(
                    workflow, "__workflow_name__", workflow.__name__)
                self._workflows[agent].update({workflow_name: workflow})
                self._workflows["*"].update({workflow_name: workflow})

    def set_services(self, services: list[Callable]) -> None:
        """Set the activity services for the WorkflowWorker instance.

        Args:
            services (list[Callable[..., ACTIVITY]]): A list of activity functions.

        Raises:
            TypeError: If any of the provided services is not of the expected type.
        """
        # Look for all the services to validate them and append them
        for service in services:
            self.__validate_service(service)
        # Override the activities list (temporal sees `services` as `activities`)
        self._activities = [*services]

    def add_services(self, services: list[Callable]) -> None:
        """Append activity services for the WorkflowWorker instance.

        Args:
            services (list[Callable[..., ACTIVITY]]): A list of activity functions to append.

        Raises:
            TypeError: If any of the provided services is not of the expected type.
        """
        # Look for all the services to validate them and append them
        for service in services:
            self.__validate_service(service)
            # Append to the activities list (temporal sees `services` as `activities`)
            self._activities.append(service)

    async def connect(self) -> tuple[Worker, Client]:
        """Connect to Temporal and initialize the Temporal worker.

        Returns:
            tuple[Worker, Client]: A tuple containing the Temporal worker instance and the Temporal
                client instance.

        Raises:
            ValueError: If there are no activities set for the worker or if the Task Queue is not
                provided.
            RuntimeError: If the worker is not properly connected to Temporal.
        """
        # Validate the GraphQL connection
        if not validate_gql_connection():
            raise RuntimeError(
                "Could not connect to the GraphQL server. Exiting...")
        # Run the Temporal worker
        if not self._activities and not self._workflows:
            raise ValueError(
                "There are no services or workflows to run in this Worker. " +
                "Append some using the method `set_services` or `set_workflows`."
            )
        # Connect to Temporal
        client, task_queue = await connect_to_temporal()
        if not task_queue or not client:
            raise ValueError("We need a Task Queue to run. Be sure to have" +
                             " a Temporal Worker running on the background" +
                             " or having the correct credentials in your .env")
        # Get the CPU-bound task queue (this is never None due to default above)
        cpu_bound_task_queue = TEMPORAL_CPU_BOUND_TASK_QUEUE

        # If you have set local workflows...
        if self._workflows:
            if self._agent in self._workflows:
                log(LogLevel.SUCCESS,
                    f"Session running with agent \x1b[1;34m{self._agent}" +
                    "\x1b[0m..."
                    )
                # Get the current workflows
                wfs = self._workflows[self._agent]
            else:
                available_wfs = [w for w in self._workflows if w != "*"]
                log(
                    LogLevel.INFO,
                    f"Agent \x1b[1;34m{self._agent}\x1b[0m not found." +
                    f" Available agents are: \x1b[1;35m{available_wfs}.\x1b[0m " +
                    "Using the default agent \x1b[1;34m'*'\x1b[0m."
                )
                # Get the current workflows
                wfs = self._workflows["*"]
            report_current_workflows(wfs)
            ValiotPythonWorkflow.set_workflows(self._workflows["*"])
        if self._activities:
            # TODO: this still shows duplicates, but they are not actually passed to temporal
            report_current_services(self._activities)
            validate_activities_queue(self._activities)

        # Separate IO-bound and CPU-bound activities
        io_bound_activities = []
        cpu_bound_activities = []

        for activity in self._activities:
            execution_mode = getattr(
                activity, "__execution_mode__", ServiceExecutionMode.IO_BOUND)
            task_queue_name = getattr(activity, "__task_queue__", "")

            if execution_mode == ServiceExecutionMode.CPU_BOUND:
                # Only register CPU-bound activities on this worker if they're assigned to our CPU task queue
                if task_queue_name == cpu_bound_task_queue:
                    cpu_bound_activities.append(activity)
                else:
                    log(LogLevel.DEBUG,
                        f"Skipping CPU-bound service {activity.__service_name__} with task queue '{task_queue_name}' " +
                        f"(expected '{cpu_bound_task_queue}')")
            else:
                # Only register IO-bound activities on this worker if they're assigned to our main task queue
                if task_queue_name == task_queue:
                    io_bound_activities.append(activity)
                else:
                    log(LogLevel.DEBUG,
                        f"Skipping IO-bound service {activity.__service_name__} with task queue '{task_queue_name}' " +
                        f"(expected '{task_queue}')")

        # Add GQL reporting activities to IO-bound activities
        io_bound_activities.extend(self._gql_activities.get_activities())

        # Remove duplicates from activity lists
        io_bound_activities = self.__remove_activity_duplicates(
            io_bound_activities)
        cpu_bound_activities = self.__remove_activity_duplicates(
            cpu_bound_activities)

        if cpu_bound_activities:
            log(LogLevel.INFO,
                f"Found {len(cpu_bound_activities)} CPU-bound activities for task queue '{cpu_bound_task_queue}'")

        # Initialize the main Temporal Worker for workflows and IO-bound activities
        self._temporal_worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[ValiotPythonWorkflow],
            activities=io_bound_activities,
            sticky_queue_schedule_to_start_timeout=timedelta(seconds=2)
        )

        # Initialize a separate worker for CPU-bound activities if needed
        if cpu_bound_activities:
            msg_end = "workers for CPU-bound activities"
            # Determine max workers for process pool
            if self._max_cpu_workers is None:
                cpu_count = multiprocessing.cpu_count()
                # Use default of CPU count - 1 (leave one for system tasks)
                max_workers = max(1, cpu_count - 1)
                log(
                    LogLevel.INFO,
                    f"Auto-detected {cpu_count} CPUs, using {max_workers} {msg_end}"
                )
            else:
                max_workers = self._max_cpu_workers
                log(LogLevel.INFO,
                    f"Using {max_workers} {msg_end}")

            # Setup process pool and shared state manager for CPU-bound activities
            manager = multiprocessing.Manager()
            shared_state_manager = SharedStateManager.create_from_multiprocessing(
                manager)
            cpu_executor = concurrent.futures.ProcessPoolExecutor(
                max_workers=max_workers)

            # Create CPU-bound worker with separate task queue
            self._temporal_cpu_worker = Worker(
                client,
                task_queue=cpu_bound_task_queue,  # This is now guaranteed to be a string
                activities=cpu_bound_activities,
                activity_executor=cpu_executor,
                shared_state_manager=shared_state_manager,
            )

            log(LogLevel.SUCCESS,
                f"Created separate worker for {len(cpu_bound_activities)} CPU-bound activities " +
                f"on task queue '{cpu_bound_task_queue}'")

        return self._temporal_worker, client

    def __validate_service(self, service: Any) -> None:
        """Validate the service provided is an actual workflow service.

        Args:
            service (any): The service to validate.

        Raises:
            TypeError: If the service is not a @service definition.
        """
        if hasattr(service, "__is_service__") is False:
            raise TypeError(
                f"The service provided {service.__name__} is not a service type.\n" +
                "Hint: Use the ValiotWorkflow decorator `@service` in this function."
            )

    def __remove_activity_duplicates(self, activities: list[Callable]) -> list[Callable]:
        """Remove duplicates from the list of activities.

        Args:
            activities (list[Callable]): A list of activity functions.

        Returns:
            list[Callable]: A list of activity functions without duplicates.
        """
        # uniqueness based on getattr(activity, "__temporal_activity_definition").name:
        return _py.uniq_by(activities, lambda a: getattr(a, "__temporal_activity_definition").name)

    async def __gql_sync(self) -> None:
        """Synchronize the GraphQL server with the Workflows and Services.

        Raises:
            ValueError: If the GraphQL sync mode is not valid.
        """
        if self._gql_sync_mode == GqlSyncMode.SYNC:
            await self.__sync_gql_workflows()
        elif self._gql_sync_mode == GqlSyncMode.SKIP:
            log(LogLevel.WARNING, "Skipping GraphQL sync...")
        else:
            raise ValueError(
                f"Invalid GraphQL sync mode: {self._gql_sync_mode}")

    async def __sync_gql_workflows(self) -> None:
        '''Sync local workflows and services with GraphQL.
        '''
        log(LogLevel.WARNING, "🔄 Syncing workflows and services with GraphQL...")
        # get list of workflow definitions to upsert:
        wf_defs: list[WorkflowDefinition] = [
            wf.__vw_defn__ for wf in self._workflows["*"].values()
        ]
        # sync workflows
        await self._gql_activities.upsert_workflow_configs(wf_defs)

    async def __run_workflow_defn_setups(self) -> None:
        '''Run setup functions for each workflow definition (if defined).
        '''
        setup_successes: list[dict[str, Any]] = []
        setup_warns: list[dict[str, Any]] = []
        setup_errors: list[dict[str, Any]] = []
        # get workflow with setup function count for an initial log:
        setup_count = sum(
            1 for wf in self._workflows["*"].values() if wf.__vw_defn__.setup_fn)
        if setup_count == 0:
            log(LogLevel.INFO, "No setup functions found for workflows.")
            return
        log(LogLevel.WARNING,
            f"🛠️  Running setup functions for {setup_count} workflows...")
        progressbar_size = 20
        incomplete_icon: str = "⬛️"
        complete_icon: str = "⬜️"
        icons_per_progress = progressbar_size // setup_count
        current_progress = 0
        for wf in self._workflows["*"].values():
            wf_defn: WorkflowDefinition = wf.__vw_defn__
            if not wf_defn.setup_fn:
                continue
            log(LogLevel.DEBUG,
                f"Running setup for workflow {wf_defn.code}...")
            # show a progressbar-like message with ⬜️ and ▪️:
            current_progress += icons_per_progress
            left_progress = progressbar_size - current_progress
            progress_bar = f"{complete_icon * current_progress}" +\
                f"{incomplete_icon * left_progress}"
            log(LogLevel.DEBUG, f"Setup progress: {progress_bar}")
            setup_result, setup_msg = await wf_defn.setup_fn(wf_defn)
            if setup_result == SetupResult.SUCCESS or setup_result is None:
                setup_successes.append({
                    "workflow": wf_defn.code,
                    "result": SetupResult.SUCCESS,
                    "message": setup_msg
                })
                continue
            elif setup_result == SetupResult.WARNING:
                setup_warns.append({
                    "workflow": wf_defn.code,
                    "result": SetupResult.WARNING,
                    "message": setup_msg
                })
            elif setup_result == SetupResult.ERROR:
                setup_errors.append({
                    "workflow": wf_defn.code,
                    "result": SetupResult.ERROR,
                    "message": setup_msg
                })
            else:
                raise ValueError(
                    f"Unknown setup result: {setup_result} for workflow {wf_defn.code}")
        if setup_errors:
            # let's not continue running the worker if there are setup errors:
            log(LogLevel.ERROR, "Setup errors found:")
            for error in setup_errors:
                log(LogLevel.ERROR,
                    f"    - {error['workflow']}: {error['message']}")
            raise RuntimeError("Setup errors found. Exiting...")
        if setup_warns:
            log(LogLevel.WARNING, "Setup warnings:")
            for warn in setup_warns:
                log(LogLevel.WARNING,
                    f"    - {warn['workflow']}: {warn['message']}")
        # let's log as a WARNING level if setup_warns > 0,
        # or SUCCESS level if only successes (chill message with WARN and SUCCESS count):
        general_setup_state = "SUCCESS" if not setup_warns else "WARNING"
        log(LogLevel[general_setup_state],
            f"Setup completed with {len(setup_successes)} successes" +
            f" and {len(setup_warns)} warnings.")

    def enable_session_heartbeat(self) -> None:
        """Enable session heartbeat for the worker.

        This will send a heartbeat every 15 seconds to the GraphQL API
        to update the lastHeartbeatAt timestamp for the task queue worker.
        """
        self._heartbeat_enabled = True
        log(LogLevel.INFO,
            f"Session heartbeat enabled with session ID: {self._session_guid}")

    def set_version(self, version: str) -> None:
        """Set worker version for heartbeat.

        Args:
            version (str): Version to set for the worker.
        """
        self._worker_version = version
        log(LogLevel.INFO, f"Worker version set to: {version}")

    def get_version_from_toml(self) -> str:
        """Get version from pyproject.toml file.

        Returns:
            str: Version from pyproject.toml file.

        Raises:
            FileNotFoundError: If pyproject.toml file not found.
            KeyError: If version key not found in pyproject.toml.
        """
        try:
            with open("pyproject.toml", "rb") as f:
                toml_dict = tomllib.load(f)
                return toml_dict["tool"]["poetry"]["version"]
        except FileNotFoundError:
            log(
                LogLevel.ERROR,
                "Could not read version from pyproject.toml: pyproject.toml file not found."
            )
            raise
        except KeyError:
            log(LogLevel.ERROR,
                "Could not read version from pyproject.toml: 'tool.poetry.version' key not found")
            raise

    async def __run_session_heartbeat(self, task_queue: str) -> None:
        """Run session heartbeat in the background.

        Args:
            task_queue (str): Task queue to send heartbeat for.
        """
        if not self._heartbeat_enabled:
            return

        log(LogLevel.INFO,
            f"Starting session heartbeat for task queue: {task_queue}")

        first_heartbeat = True
        backoff_time = 10  # Start with 10 seconds
        max_backoff = 300  # Maximum backoff of 5 minutes (300 seconds)

        while True:
            try:
                # Trim worker_version to only numbers (e.g., '1.4.0' from '1.4.0rc1')
                trimmed_version = None
                if self._worker_version and isinstance(self._worker_version, str):
                    match = re.match(r'(\d+\.\d+\.\d+)', self._worker_version)
                    if match:
                        trimmed_version = match.group(1)
                    else:
                        trimmed_version = self._worker_version  # fallback if no match
                await self._gql_activities.heartbeat_task_queue_worker(
                    session_guid=self._session_guid,
                    task_queue=task_queue,
                    worker_version=trimmed_version
                )

                if first_heartbeat:
                    log(LogLevel.DEBUG, "First heartbeat sent successfully")
                    first_heartbeat = False

                # Reset backoff time on successful heartbeat
                if backoff_time > 10:
                    log(LogLevel.DEBUG, "Heartbeat recovered")
                    backoff_time = 10

                # Wait for 10 seconds before sending the next heartbeat
                # This will raise CancelledError if the task is cancelled during sleep
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                log(LogLevel.INFO, "Heartbeat task cancelled")
                raise
            except Exception as e:
                log(LogLevel.ERROR, f"Error sending heartbeat: {e}")
                log(LogLevel.WARNING,
                    f"Heartbeat failed, retrying in {backoff_time} seconds")

                # Wait for the current backoff time
                await asyncio.sleep(backoff_time)

                # Exponential backoff with a maximum limit
                backoff_time = min(backoff_time * 2, max_backoff)

    async def run(self) -> None:
        """Run the Temporal worker.

        Raises:
            RuntimeError: If the worker is not properly connected to Temporal.
        """
        if self._temporal_worker is None:
            raise RuntimeError(
                "The worker is not connected to Temporal. " +
                "Please run `connect` method first."
            )
        # setup
        await self.__gql_sync()
        await self.__run_workflow_defn_setups()

        # Run the heartbeat task if enabled
        heartbeat_task = None
        if self._heartbeat_enabled:
            task_queue = self._temporal_worker.task_queue
            heartbeat_task = asyncio.create_task(
                self.__run_session_heartbeat(task_queue)
            )

        try:
            if self._temporal_cpu_worker:
                log(LogLevel.INFO, "Starting IO-bound and CPU-bound workers")
            else:
                log(LogLevel.INFO, "Starting IO-bound worker")
            # Run the worker(s)
            log(LogLevel.INFO, "Waiting for triggers to execute workflows...")
            if self._temporal_cpu_worker:
                # Run both workers in parallel
                await asyncio.gather(
                    self._temporal_worker.run(),
                    self._temporal_cpu_worker.run()
                )
            else:
                # Run just the main worker
                await self._temporal_worker.run()
        finally:
            # Cancel the heartbeat task if it's running
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
            # redis cleanup:
            if has_async_client_instance():
                # get the async client:
                async_client = get_async_client_instance()
                if async_client is None:
                    raise RuntimeError("Async Redis client is not available.")
                # perform the cleanup:
                await async_client.close()
            if has_sync_client_instance():
                # get the sync client:
                sync_client = get_sync_client_instance()
                if sync_client is None:
                    raise RuntimeError("Sync Redis client is not available.")
                # perform the cleanup:
                sync_client.close()
