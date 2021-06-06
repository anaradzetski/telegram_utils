"""Utils"""
import inspect
from functools import wraps
from telegram.ext import Handler, Dispatcher


class HandlerRegister:
    """Class for registering handlers by decorating callback functions"""

    def __init__(self):
        self.__handlers_lst = []

    def register(self, handler_cls: Handler, *args, **kwargs):
        """Registers callable object to be handled be used as handler.

        Args:
            cls:
                name of Handler or a Handler class. If handler
                decorator is used, than function will be registred as
                `cls` callback.
            args, kwargs:
                args and kwargs for creating `handler_cls` instance.
        """
        def ret_dec(obj):
            sig = inspect.signature(obj)
            param_names = list(sig.parameters.keys())
            if (
                len(param_names) != 2 or
                param_names[0] != 'update' or
                param_names[1] != 'context'
            ):
                raise ValueError('Handler callback should have two params: update and context')

            @wraps(obj)
            def ret_obj(update, context):
                return obj(update, context)
            self.__handlers_lst.append(handler_cls(*args, **kwargs, callback=ret_obj))

            return ret_obj

        return ret_dec

    def add(self, dispatcher: Dispatcher):
        """Adds handlers to a dispathcher"""
        for handler in self.__handlers_lst:
            dispatcher.add_handler(handler)
