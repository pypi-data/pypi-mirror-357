"""
Include different mutations that are going to be used
in the update of the Workflow Run Events and ServiceRunProgress
"""

UPDATE_PROGRESS = """
mutation updateServiceRunProgress($serviceRunId: ID!, $progress: Int!) {
  updateWorkflowServiceRun(
    id: $serviceRunId
    workflowServiceRun: {progress: $progress}
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
      progress
    }
  }
}
"""

SEND_WORKFLOW_RUN_EVENT = """
mutation sendWorkflowRunEvent(
  $workflowRunId: ID!,
  $eventCode: String!,
  $emitterTokenId: ID,
  $payload: Jsonb!
) {
  createWorkflowRunEvent(
    workflowRunId: $workflowRunId
    eventCode: $eventCode
    emitterTokenId: $emitterTokenId
    payload: $payload
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
