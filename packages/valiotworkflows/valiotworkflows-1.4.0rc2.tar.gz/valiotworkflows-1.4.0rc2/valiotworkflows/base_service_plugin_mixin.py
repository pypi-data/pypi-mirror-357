"""
Include the BaseServicePluginMixin class that will be used as a base class for the PluginMixins.
"""
from typing import Union, TypeVar
from .service_handler_base import ServiceHandlerBase

T = TypeVar('T')

class BaseServicePluginMixin(ServiceHandlerBase):
    """
    Base class for the PluginMixins.
    It exposes the public methods and private attributes that can be used
    by the custom PluginMixins.

    Note: The plugin may contain additional methods that will be added to
    the ServiceHandler on Plugin registration.
    This may be helpful to extend the ServiceHandler's functionality.

    IMPORTANT: The plugin class won't actually be instantiated,
    it will rather have it's methods added to the ServiceHandler class
    and it's pre/post methods called with the ServiceHandler's instance.
    This means, that the plugin class won't have it's __init__ method called.

    Attributes
    ----------
    pre_service : fn() -> None
        may act as an __init__ method of sorts
        Whatever code needs to be run before the service's body, should be placed here.

    post_service : fn(response: Union[dict, None] = None) -> Union[dict, None]
        may act as a middleware for updating the response before it's sent back to the
            Workflows Worker.
        Whatever code needs to be run after the service's body,
        before giving the control back to the Workflow Worker, should be placed here.

    """
    async def pre_service(self):
        """
        may act as an __init__ method of sorts.
        Whatever code needs to be run before the service's body, should be placed here.
        """

    # may act as a middleware for updating the response before
    # it's sent back to the Workflows Worker:
    async def post_service(self, response: Union[T, dict, None] = None):
        """May act as a middleware for updating the response before it's sent
        back to the Workflows Worker.
        Whatever code needs to be run after the service's body,
        before giving the control back to the Workflow Worker, should be placed here.

        Parameters
        ----------
        response : Union[dict, None]
            The response of the service's body

        Returns
        -------
        Union[dict, None]
            The updated response of the service's body
        """
        return response

    # ! additional methods will be added to the ServiceHandler on Plugin registration:
    # ! usage: handler.my_custom_method()
    # def my_custom_method(self):
    #     pass
