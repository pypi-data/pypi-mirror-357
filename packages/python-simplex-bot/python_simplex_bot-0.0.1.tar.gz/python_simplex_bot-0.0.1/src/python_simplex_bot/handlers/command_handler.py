from python_simplex_bot.types import BaseContext, BaseHandler
import re


def command_handler(command: str|re.Pattern):
    """
    Handle command messages
    """
    def wrapper(handler: BaseHandler):
        async def inner(message: str, context: BaseContext):
            if isinstance(command, str):
                if message.startswith(command):
                    return await handler(message, context)
            elif isinstance(command, re.Pattern):
                if command.match(message):
                    return await handler(message, context)
        return inner
    return wrapper
