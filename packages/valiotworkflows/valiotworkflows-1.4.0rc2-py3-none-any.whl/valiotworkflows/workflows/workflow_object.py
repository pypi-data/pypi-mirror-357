"""
Just define the workflowObject as a dataclass to be able to serialize and deserialize the data.

# TODO: Would be good to include custom methods for the dataclasses, like __str__ and __repr__
# or even the __hash__ method.
"""

from dataclasses import dataclass

# https://github.com/temporalio/sdk-python/blob/main/README.md#data-conversion
# it basically needs a dataclass to be able to serialize and deserialize the data.
# if we ever need something more complex, we can use the DataConverter interface
workflowObject = dataclass
