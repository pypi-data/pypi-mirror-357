# mylibrary/testing.py
import inspect
from typing import Generic, TypeVar, Union
from .. import ServiceHandler
from unittest.mock import Mock

T = TypeVar('T')

class MockServiceHandler(ServiceHandler[T]):
    def __init__(self, context: Union[dict, None], event: dict, meta: dict, lifecycle: str = None, input: T = None):
        # Initialize the real ServiceHandler with the required context
        super().__init__(context, event, meta, lifecycle, input)

        # Mock specific methods while copying their signatures from the real class
        self.update_progress = self._create_mock_with_signature('update_progress')
        self.heartbeat = self._create_mock_with_signature('heartbeat')
        self.send_event = self._create_mock_with_signature('send_event')

    def _create_mock_with_signature(self, method_name):
        # Retrieve the original method from the parent class
        real_method = getattr(super(), method_name)

        # Extract the method signature
        real_signature = inspect.signature(real_method)

        # Create a mock function
        mock_func = Mock()

        # Use the same signature on the mock while ensuring it behaves like a mock
        def wrapped_mock(*args, **kwargs):
            # Ensure the arguments match the original method's signature
            bound_args = real_signature.bind(*args, **kwargs)
            bound_args.apply_defaults()  # Ensure default arguments are respected

            # Call the underlying mock (this allows tracking calls and other mock functionality)
            return mock_func(*args, **kwargs)

        # Attach the mock to the returned wrapped function so that it has `call_count` and other mock attributes
        wrapped_mock.mock = mock_func

        return wrapped_mock