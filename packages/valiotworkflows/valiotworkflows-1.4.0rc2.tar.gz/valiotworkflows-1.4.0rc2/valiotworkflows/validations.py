"""
Include the file for some vaidations, as the GQL validations
and the TemporalIO validations.
"""
import os
import traceback
from valiotlogging import log, LogLevel

# Local imports
from .config import setup_gql

# TODO: Implement directly in gql client (pygqlc)
# as gql.validate_environment(env_name?: str)


class QueryException(Exception):
    """Exception raised when a query fails."""


GET_TOKEN_VALIDATION = '''
mutation authorizeToken(
  $token: String!
) {
  authorizeToken (
    token: $token
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
'''

gql = setup_gql()


def validate_gql_connection(token_var_name: str = 'TOKEN'):
    """
    Validates the GraphQL connection.

    Returns
    -------
    bool
        True if the connection is valid, False otherwise
    """
    try:
        if not "ENV" in os.environ:
            raise RuntimeError(
                "\"ENV\" environment variable not found, " +
                "please set one (usually \"dev\" or \"prod\")."
            )
        data, errors = gql.query(GET_TOKEN_VALIDATION, {
            # remove the "Bearer " prefix from the token
            'token': os.getenv(token_var_name, "").split(' ')[1]
        })
        if errors:
            raise QueryException(errors)
        if not data.get('successful'):
            raise QueryException(data.get('messages'))
        log(LogLevel.SUCCESS,
            f'Connected to the GraphQL server ({os.getenv("API")})')
        return True
    except QueryException as e:
        if os.getenv("LOGGING_STYLE") == "DEBUG":
            traceback.print_exc()
        else:
            log(LogLevel.ERROR, 'Could not connect to the GraphQL server. Exiting...')
            raise e
        log(LogLevel.ERROR, 'Could not connect to the GraphQL server. Exiting...')
        return False
