'''Plugin that eases connection from Services to GraphQL via subscriptions
'''

from valiotlogging import LogLevel
from ..base_service_plugin_mixin import BaseServicePluginMixin


class GraphQLSubPlugin(BaseServicePluginMixin):

    async def pre_service(self):
        self._active_gql_subs = getattr(self, '_active_gql_subs', [])
        self._subbed_to_workflow_run_finished = getattr(
            self, '_subbed_to_workflow_run_finished', False)
        self._unsub_workflow_run = getattr(self, '_unsub_workflow_run', None)

    async def post_service(self, response: dict = None):
        return response

    def gql_subscribe(self, query, variables=None, callback=None):
        """Subscribe to a GraphQL query.

        Args:
            query (str): The GraphQL query to subscribe to.
            callback (Callable): The callback function to be called
            when the subscription is triggered.

        Returns:
            None
        """
        unsub = self._gql.subscribe(query, variables, callback)
        self._active_gql_subs.append(unsub)
        if not self._subbed_to_workflow_run_finished:
            self._sub_to_workflow_run_finished()
            self._subbed_to_workflow_run_finished = True

    def _sub_to_workflow_run_finished(self):
        """Subscribe to the workflow run finished event.

        Args:
            callback (Callable): The callback function to be called when the subscription is triggered.

        Returns:
            None
        """

        # TODO: change this based on the self.lifecycle:
        LIFECYCLE_FINISHED_SUB = ""

        if self._lifecycle == "WORKFLOW_RUN":
            LIFECYCLE_FINISHED_SUB = """
                subscription workflowRunFinished($workflowRunId: ID!) {
                        workflowRunUpdated(filter: {id: $workflowRunId, not: {finishedAt: null}}) {
                            successful
                        }
                    }
            """
        elif self._lifecycle == "STATE_RUN":
            LIFECYCLE_FINISHED_SUB = """
                subscription stateRunFinished($stateRunId: ID!) {
                    workflowStateRunUpdated(filter: {id: $stateRunId, not: {leftAt: null}}) {
                        successful
                        result {id leftAt}
                    }
                }
            """
        else:
            raise Exception(f'invalid lifecycle: {self._lifecycle}')
        # use the lifecycle_run_id as the unique id for the subscription:
        lifecycle_id_field = "workflowRunId" if self._lifecycle == "WORKFLOW_RUN" else "stateRunId"
        lifecycle_name = "workflowRun" if self._lifecycle == "WORKFLOW_RUN" else "stateRun"
        lifecycle_run_id = self._meta.get(lifecycle_id_field)
        if lifecycle_run_id is None:
            raise Exception(
                f'{lifecycle_id_field} not found in meta fields of service handler')
        variables = {lifecycle_id_field: lifecycle_run_id}

        def callback_unsub_all(_data):
            self._unsub_all_active_gql_subs()
            # TODO: request cancellation for the subscription to workflow_run finished:
            # self.log(LogLevel.INFO, 'requesting cancellation of workflow run finished subscription...')
            # self._workflow_run_finished_event.set()
        self._unsub_workflow_run = self._gql.subscribe(
            LIFECYCLE_FINISHED_SUB, variables, callback_unsub_all)  # _id=sub_id)
        self.log(LogLevel.INFO, f'subscribed to {lifecycle_name} finished')

    def _unsub_all_active_gql_subs(self):
        """Unsubscribe from all active subscriptions.

        Returns:
            None
        """
        lifecycle_name = "workflowRun" if self._lifecycle == "WORKFLOW_RUN" else "stateRun"
        self.log(
            LogLevel.INFO, f'{lifecycle_name} finished: unsubscribing from all active subscriptions')
        for unsub in self._active_gql_subs:
            unsub()
        self._active_gql_subs = []
