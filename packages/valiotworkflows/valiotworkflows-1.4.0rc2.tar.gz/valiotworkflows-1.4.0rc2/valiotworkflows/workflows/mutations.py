"""
Mutations to be used in all the Workflows GQL Activities
updates, upserts and creations.
"""

GET_WORKFLOW_CONFIG = """
  query GET_WORKFLOW_CONFIG($workflowCode: String!) {
    workflow(findBy: { code: $workflowCode }) {
      id
      name
      code
      enabled
      initialStateId
      trigger
      config
      taskQueueId
      services(orderBy: { asc: ID }) {
        id
        name
        code
        isAlwaysOn
        taskQueueId
      }
      states(orderBy: { asc: ID }) {
        id
        code
        invoke {
          id
          stateId
          type
          taskQueueId
          service {
            id
            name
            code
            isAlwaysOn
            taskQueueId
          }
          with
          serviceId
          workflowId
        }
        nameI18nKey
        descriptionI18nKey
        type
        actionType
        actionLink
        fromTransitions(orderBy: { asc: ID }) {
          id
          eventId
          fromStateId
          toStateId
        }
        toTransitions(orderBy: { asc: ID }) {
          id
          config
          eventId
          fromStateId
          toStateId
        }
      }
    }
  }
"""

GET_WORKFLOW_CONFIGS = '''
query workflowConfigs(
  $workflowCodes: [String!]
){
  workflows(
    filter: { codes: $workflowCodes }
    orderBy: {desc: ID}
  ) {
    id
    name
    code
    handleSchema
    enabled
    trigger
    config
    taskQueue {id code}
    initialState {id code}
    states(orderBy: {asc: ID}){id code}
    events (orderBy: {asc: ID}){
      id
      payloadSchema
      event{id name code}
    }
    services(orderBy: {asc: ID}) {
      id
      name
      code
    }
  }
}
'''

GET_TASK_QUEUES = """
query taskQueues {
  taskQueues(orderBy: { asc: CODE }) {
    id
    queueKind
    name
    code
  }
}
"""

WORKFLOW_EVENTS = """
  query WorkflowEvents($workflowId: ID, $workflowCode: String) {
    workflowEvents(
      orderBy: { asc: ID }
      filter: { not: { eventId: null }, workflowCode: $workflowCode, workflowId: $workflowId }
    ) {
      id
      workflowId
      event {
        id
        code
      }
      payloadSchema
    }
  }
"""

UPSERT_BULK_TASK_QUEUES = """
mutation upsertBulkTaskQueues(
  $taskQueues: [UpsertBulkTaskQueueParams]
) {
  upsertBulkTaskQueues(
    taskQueues: $taskQueues
  ){
    successful
    messages {
      field
      message
    }
    result {
      taskQueues {
        id
      }
    }
  }
}
"""

UPSERT_BULK_WORKFLOW_EVENT_CATALOGS = """
mutation upsertBulkWorkflowEventCatalogs(
  $workflowEventCatalogs: [UpsertBulkWorkflowEventCatalogParams]
) {
  upsertBulkWorkflowEventCatalogs(
    workflowEventCatalogs: $workflowEventCatalogs
  ){
    successful
    messages {
      field
      message
    }
    result {
      workflowEventCatalogs {
        id
        code
      }
    }
  }
}
"""

UPSERT_BULK_WORKFLOW_CATEGORIES = """
mutation upsertBulkWorkflowCategories(
  $workflowCategories: [UpsertBulkWorkflowCategoryParams]
) {
  upsertBulkWorkflowCategories(
    workflowCategories: $workflowCategories
  ){
    successful
    messages {
      field
      message
    }
    result {
      workflowCategories {
        id
        code
      }
    }
  }
}
"""

UPSERT_BULK_WORKFLOW_WORKFLOW_CATEGORIES = """
mutation upsertBulkWorkflowWorkflowCategories(
  $workflowWorkflowCategories: [UpsertBulkWorkflowWorkflowCategoryParams]
) {
  upsertBulkWorkflowWorkflowCategories(
    workflowWorkflowCategories: $workflowWorkflowCategories
  ) {
    successful
    messages {
      field
      message
    }
    result {
      workflowWorkflowCategories {
        id
        workflowId
        categoryId
      }
    }
  }
}
"""

UPSERT_BULK_WORKFLOWS = """
mutation upsertBulkWorkflows(
  $workflows: [UpsertBulkWorkflowParams]
){
  upsertBulkWorkflows(
    workflows: $workflows
  ){
    successful
    messages {
      field
      message
    }
    result {
      workflows {
        id
        code
        states {
            id
            code
        }
      }
    }
  }
}
"""

CREATE_WORKFLOW_RUN = """
mutation CreateWorkflowRun(
  $workflowCode: String!
  $context: Jsonb
  $rawHandle: Jsonb!
  $startedAt: DateTime!
  $taskQueue: String
  $parentWorkflowRunId: ID
  $parentStateRunId: ID
) {
  createWorkflowRun(
    workflowCode: $workflowCode
    context: $context
    rawHandle: $rawHandle
    startedAt: $startedAt
    taskQueueCode: $taskQueue
    parentWorkflowRunId: $parentWorkflowRunId
    parentStateRunId: $parentStateRunId
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
    }
  }
}
"""

UPDATE_WORKFLOW_LAST_RUN_AT = """
mutation updateWorkflowLastRunAt($workflowCode: String!) {
  updateWorkflow(
    findBy: { code: $workflowCode }
    workflow: {
      lastRunAt: "now()"
    }
  ){
    successful
    messages{ field message }
    result {
      id
      lastRunAt
    }
  }
}
"""

FINISH_WORKFLOW_RUN = """
mutation finishWorkflowRun($workflowRunId: ID!, $finishedAt: DateTime!) {
    updateWorkflowRun(id: $workflowRunId, workflowRun: { finishedAt: $finishedAt }) {
      successful
      result {
        id
        finishedAt
      }
    }
  }
"""

CREATE_CHILD_WORKFLOW_RUN = """
mutation CreateChildWorkflowRun(
  $workflowCode: String!
  $context: Jsonb
  $rawHandle: Jsonb!
  $parentStateRunId: ID!
  $parentWorkflowRunId: ID!
  $startedAt: DateTime!
  $taskQueue: String
) {
  createWorkflowRun(
    workflowCode: $workflowCode
    context: $context
    rawHandle: $rawHandle
    parentStateRunId: $parentStateRunId
    parentWorkflowRunId: $parentWorkflowRunId
    startedAt: $startedAt
    taskQueueCode: $taskQueue
  ) {
    successful
    result {
      id
    }
    messages {
      field
      message
    }
  }
}
"""

ATTACH_WORKFLOW_RUN_TO_INIT_EVENT = """
mutation AttachWorkflowRunToEvent($workflowRunId: ID!, $eventId: ID!, $acknowledge: Jsonb!) {
  updateWorkflowRunEvent(id: $eventId, workflowRunEvent: { workflowRunId: $workflowRunId, response: $acknowledge }) {
    successful
    messages {
      field
      message
    }
    result {
      id
    }
  }
}
"""

UPSERT_STATE_RUN = """
  mutation enterWorkflowToState($stateId: ID!, $workflowRunId: ID!, $enteredAt: DateTime!) {
    upsertWorkflowStateRun(
      findBy: { stateId: $stateId, workflowRunId: $workflowRunId, enteredAt: $enteredAt }
      workflowStateRun: { currentAtWorkflowRunId: $workflowRunId }
    ) {
      successful
      result {
        id
      }
    }
  }
"""

# TODO: gql activity for this (reports current service being executed)
UPSERT_SERVICE_RUN_TO_STATE_RUN = """
  mutation upsertServiceRunToStateRun($stateRunId: ID!, $serviceId: ID!, $taskQueue: String) {
    upsertWorkflowServiceRun(
      findBy: { stateRunId: $stateRunId }
      workflowServiceRun: { serviceId: $serviceId, status: RUNNING, progress: 0, taskQueueCode: $taskQueue }
    ) {
      successful
      messages {
        field
        message
      }
      result {
        id
      }
    }
  }
"""

CREATE_STATE_RUN_WITH_SERVICE = """
mutation enterWorkflowToState(
  $stateId: ID!
  $workflowRunId: ID!
  $enteredAt: DateTime!
  $createServiceRun: CreateWorkflowServiceRunParams
) {
  createWorkflowStateRun(
    stateId: $stateId
    workflowRunId: $workflowRunId
    currentAtWorkflowRunId: $workflowRunId
    enteredAt: $enteredAt
    createInvokedServiceRun: $createServiceRun
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
      invokedServiceRun {
        id
      }
    }
  }
}
"""

CREATE_STATE_RUN_WITH_WORKFLOW_RUN_UPDATE = """
mutation exitState($stateId: ID!, $workflowRunId: ID!, $enteredAt: DateTime!) {
  createWorkflowStateRun(
    stateId: $stateId
    workflowRunId: $workflowRunId
    currentAtWorkflowRunId: $workflowRunId
    enteredAt: $enteredAt
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
    }
  }
  updateWorkflowRun(id: $workflowRunId, workflowRun: { finishedAt: $enteredAt }) {
    successful
    messages {
      field
      message
    }
    result {
      id
      finishedAt
    }
  }
}
"""

CREATE_SERVICE_RUN = """
mutation CreateServiceRun($serviceId: ID!, $stateRunId: ID!, $taskQueue: String) {
  createWorkflowServiceRun(progress: 0, serviceId: $serviceId, stateRunId: $stateRunId, taskQueueCode: $taskQueue) {
    successful
    messages {
      message
      field
    }
    result {
      id
    }
  }
}
"""

FINISH_STATE_RUN = """
  mutation finishStateRuns($workflowRunId: ID!, $fromStateId: ID!, $leftAt: DateTime!) {
    # PLURAL to enforce we clear up at least 1 stateRun from being the current one.
    # but it could be 0 if this is run at a retry, or 2+ if there was an error upstream
    # which caused more than 1 stateRun to be created
    updateWorkflowStateRuns(
      filter: { workflowRunId: $workflowRunId, currentAtWorkflowRunId: $workflowRunId, stateId: $fromStateId }
      workflowStateRun: { currentAtWorkflowRunId: null, leftAt: $leftAt }
    ) {
      successful
      messages {
        field
        message
      }
      result {
        workflowStateRuns {
          id
        }
      }
    }
  }
"""

FINISH_SERVICE_RUN = """
mutation FinishServiceRun($serviceRunId: ID, $endAt: DateTime!) {
  updateWorkflowServiceRun(id: $serviceRunId, workflowServiceRun: { endAt: $endAt, status: FINISHED }) {
    successful
    messages {
      field
      message
    }
    result {
      id
    }
  }
}
"""

UPDATE_CONTEXT = """
mutation updateContext($workflowRunId: ID, $context: Jsonb) {
  updateWorkflowRun(id: $workflowRunId, workflowRun: { context: $context }) {
    successful
    messages {
      field
      message
    }
    result {
      id
    }
  }
}
"""

UPDATE_WORKFLOW_SCHEDULE_STATUS = """
mutation updateWorkflowScheduleStatus($code: String!, $enabled: Boolean!) {
  updateWorkflow(findBy: { code: $code }, workflow: { enabled: $enabled }) {
    successful
    messages {
      field
      message
    }
    result {
      id
      code
      enabled
    }
  }
}
"""

UPDATE_WORKFLOW_CONFIG = """
mutation UpdateWorkflowConfig($code: String!, $path: String!, $value: Jsonb!) {
  updateWorkflow(findBy: { code: $code }, updateConfig: { set: { path: [$path], value: $value } }) {
    successful
    messages {
      message
    }
  }
}
"""

UPDATE_WORKFLOW_RUN_EVENT = """
mutation updateWorkflowRunEvent(
  $id: ID!
  $response: Jsonb!
  $workflowRunId: ID
) {
  updateWorkflowRunEvent(
    id: $id
    workflowRunEvent: {
      workflowRunId: $workflowRunId
      response: $response
    }
  ){
    successful
    messages { field message }
    result { id emitterTokenId payload }
  }
}
"""

CREATE_WORKFLOW_RUN_EVENT = """
mutation createWorkflowRunEvent(
  $workflowRunId: ID!
  $eventCode: String!
  $emitterTokenId: ID
  $payload: Jsonb!
  $response: Jsonb!
) {
  createWorkflowRunEvent(
    workflowRunId: $workflowRunId
    eventCode: $eventCode
    emitterTokenId: $emitterTokenId
    payload: $payload
    response: $response
  ) {
    successful
    messages { field message }
    result { id emitterTokenId payload }
  }
}
"""

TASK_QUEUE_WORKER_HEARTBEAT = """
mutation taskQueueWorkerHeartbeat(
  $sessionGuid: String!
  $taskQueue: String!
  $workerVersion: String
) {
  upsertTaskQueueWorker(
    findBy: {
      workerSessionGuid: $sessionGuid
    }
    taskQueueWorker: {
      taskQueueCode: $taskQueue
      version: $workerVersion
      lastHeartbeatAt: "now()"
    }
  ){
    successful
    messages {field message}
    result{
      id
      workerSessionGuid
      lastHeartbeatAt
      version
    }
  }
}
"""
