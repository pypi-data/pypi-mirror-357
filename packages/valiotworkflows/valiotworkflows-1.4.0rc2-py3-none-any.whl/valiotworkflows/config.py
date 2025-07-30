"""
Configuration methods for the Workflows implementation
on Python services
"""
import os
import base64
from valiotlogging import LogLevel, log
from temporalio.client import Client, TLSConfig  # type: ignore
from pygqlc import GraphQLClient


async def connect_to_temporal():
    """Connects to the Temporal's task queue server.

    For Local Temporal dev-server, using the following environment variables:
    - TEMPORAL_CLOUD_ENDPOINT: Temporal dev-server task-queue endpoint (e.g. 127.0.0.1:7233)
    - TEMPORAL_CLOUD_NAMESPACE: Temporal dev-server namespace (e.g. "default")
    - TEMPORAL_TASK_QUEUE: Temporal dev-server task queue (e.g. "activities-task-queue")

    For Temporal Cloud, using the following environment variables:
    - TEMPORAL_CLOUD_ENDPOINT: Temporal's endpoint (e.g. default-development.ab1c2.tmprl.cloud:7233)
    - TEMPORAL_CLOUD_NAMESPACE: Temporal's namespace (e.g. default-development.ab1c2)
    - TEMPORAL_TASK_QUEUE: Temporal's task queue (e.g. activities-task-queue)
    - TEMPORAL_CLIENT_CERT: base64 encoded certificate (starts with "LS0tLS1CRUdJTiB",
        as it's a base64 encoded string)
    - TEMPORAL_CLIENT_PRIVATE_KEY: base64 encoded private key (starts with "LS0tLS1CRUdJTiB",
        as it's a base64 encoded string)

    Returns
    -------
    temporalio.client.Client
        The Temporal's client
    str
        The Temporal's task queue
    """
    # Connect to Temporal
    env_vars = {
        "TEMPORAL_CLOUD_ENDPOINT": os.getenv("TEMPORAL_CLOUD_ENDPOINT", ""),
        "TEMPORAL_CLOUD_NAMESPACE": os.getenv("TEMPORAL_CLOUD_NAMESPACE", ""),
        "TEMPORAL_TASK_QUEUE": os.getenv("TEMPORAL_TASK_QUEUE", ""),
        "TEMPORAL_CPU_BOUND_TASK_QUEUE": os.getenv(
            "TEMPORAL_CPU_BOUND_TASK_QUEUE",
            "default-cpu-bound-task-queue"),
        "TEMPORAL_CLIENT_CERT": os.getenv("TEMPORAL_CLIENT_CERT", ""),
        "TEMPORAL_CLIENT_PRIVATE_KEY": os.getenv("TEMPORAL_CLIENT_PRIVATE_KEY", ""),
    }

    # Validate environment variables
    dev_mode = validate_env_vars(env_vars)
    try:
        # Connect to local Temporal dev-server
        if dev_mode == "local":
            client = await Client.connect(
                env_vars["TEMPORAL_CLOUD_ENDPOINT"],
                namespace=env_vars["TEMPORAL_CLOUD_NAMESPACE"],
            )
            log(
                LogLevel.SUCCESS,
                f'Connected to the temporal.io server ({os.getenv("TEMPORAL_CLOUD_ENDPOINT")})'
            )
            log(LogLevel.INFO,
                f'IO-bound task queue: {env_vars["TEMPORAL_TASK_QUEUE"]}')
            log(LogLevel.INFO,
                f'CPU-bound task queue: {env_vars["TEMPORAL_CPU_BOUND_TASK_QUEUE"]}')
            return client, env_vars["TEMPORAL_TASK_QUEUE"]
        # Connect to Temporal Cloud
        tls_config = TLSConfig(
            client_cert=base64.b64decode(env_vars["TEMPORAL_CLIENT_CERT"]),
            client_private_key=base64.b64decode(
                env_vars["TEMPORAL_CLIENT_PRIVATE_KEY"]),
        )
        client = await Client.connect(
            env_vars["TEMPORAL_CLOUD_ENDPOINT"],
            namespace=env_vars["TEMPORAL_CLOUD_NAMESPACE"],
            tls=tls_config,
        )
        log(
            LogLevel.SUCCESS,
            f'Connected to the temporal.io server ({os.getenv("TEMPORAL_CLOUD_ENDPOINT")})'
        )
        log(
            LogLevel.INFO,
            f'Task queue: {env_vars["TEMPORAL_TASK_QUEUE"]}'
        )
        return client, env_vars["TEMPORAL_TASK_QUEUE"]
    except Exception as e:  # pylint: disable=W0718
        log(LogLevel.ERROR, 'Could not connect to Temporal. Exiting...')
        raise e


def setup_gql():
    '''
    Sets up the GraphQL client based on the environment variables:
    - ENV: environment name (e.g. dev, prod)
    - API: GraphQL API URL (e.g. https://test.valiot.app/)
    - WSS: GraphQL WSS URL (e.g. wss://test.valiot.app/)
    - TOKEN: GraphQL token (e.g. "Bearer 1234567890")
    '''
    gql = GraphQLClient()
    gql.addEnvironment(
        os.environ.get('ENV'),
        url=os.environ.get('API'),
        wss=os.environ.get('WSS'),
        headers={'Authorization': os.environ.get('TOKEN')})
    # ! Sets the environment selected in the .env file
    gql.setEnvironment(os.environ.get('ENV'))
    return gql


def validate_env_vars(env_vars: dict):
    """Validates the environment variables and raises an error if configuration is incorrect.
    For local development, it should include the following environment variables:
    - TEMPORAL_CLOUD_ENDPOINT: pointing to 127.0.0.1:####
    - TEMPORAL_CLOUD_NAMESPACE: any string (if not set, it will use "default")
    - TEMPORAL_TASK_QUEUE: any string (if not set, it will use "activities-task-queue")

    For cloud environment, it should include the following environment variables:
    - TEMPORAL_CLOUD_ENDPOINT: pointing to <alphanumeric-string>.<5-chars>.tmprl.cloud:####
    - TEMPORAL_CLOUD_NAMESPACE: pointing to <alphanumeric-string>.<5-chars>
    - TEMPORAL_TASK_QUEUE: any string (if not set, it will use "activities-task-queue")
    - TEMPORAL_CLIENT_CERT: base64 encoded certificate
        (starts with "LS0tLS1CRUdJTiB", as it's a base64 encoded string)
    - TEMPORAL_CLIENT_PRIVATE_KEY: base64 encoded private key
        (starts with "LS0tLS1CRUdJTiB", as it's a base64 encoded string)

    The function returns a string (either "local" or "cloud") that
    indicates the environment type and raises an error if configuration
    is incorrect (explaining which variables are missing or incorrect).
    """
    base_vars = [
        "TEMPORAL_CLOUD_ENDPOINT",
        "TEMPORAL_CLOUD_NAMESPACE",
        "TEMPORAL_TASK_QUEUE",
    ]
    cloud_vars = [
        "TEMPORAL_CLIENT_CERT",
        "TEMPORAL_CLIENT_PRIVATE_KEY",
    ]
    # validate correct base environment variables
    missing_base_vars = [key for key in base_vars if not env_vars.get(key)]
    if missing_base_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_base_vars)}")
    # validate if env configuration is for local or cloud
    endpoint: str = env_vars.get("TEMPORAL_CLOUD_ENDPOINT", "")
    local_prefixes = ["localhost", "127.0.0.1"]
    if any(local_pre in endpoint for local_pre in local_prefixes):
        return "local"
    # validate correct cloud environment variables
    missing_cloud_vars = [key for key in cloud_vars if not env_vars.get(key)]
    if missing_cloud_vars:
        raise ValueError(
            f"Missing required cloud environment variables: {', '.join(missing_cloud_vars)}"
        )
    # TODO: validate format of cloud variables
    # !(e.g. TEMPORAL_CLOUD_ENDPOINT should be
    # !<alphanumeric-string>.<5-chars>.tmprl.cloud:####)
    return "cloud"
