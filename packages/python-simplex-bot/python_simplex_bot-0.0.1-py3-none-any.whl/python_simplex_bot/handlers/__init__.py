from .text_handler import text_handler
from .command_handler import command_handler
from python_simplex_bot.types import BaseHandler, BaseContext, Update, UpdateNewContact, UpdateTextMessage
import re


__all__ = ["text_handler", "command_handler"]

class MessageHandlersTrait:
    _handlers = []
    
    async def _handle(self, update: Update|None, context: BaseContext):
        print("\033[1;32m _handle \033[m", update, context)
        if update is None:
            return False
        for handler in self._handlers:
            if await handler(update, context):
                return True
        return False
    
    def hello_handler(self, handler_func: BaseHandler):
        """
        Add a hello handler to the bot
        """
        async def wrapper(update: Update, context: BaseContext):
            if not isinstance(update, UpdateNewContact):
                return False
            await handler_func(update, context)
            return True
        self._handlers.append(wrapper)
        return wrapper

    def text_handler(self, handler_func: BaseHandler):
        """
        Add a text handler to the bot

        Usage:
        @bot.text_handler
        async def handle_text(message: str, context: BaseContext):
            print(message)
            print(context)
            await context.reply("You entered: " + message)
        """
        async def wrapper(update: Update, context: BaseContext):
            if not isinstance(update, UpdateTextMessage):
                return False
            await handler_func(update, context)
            return True
        self._handlers.append(wrapper)
        return wrapper

    def command_handler(self, command: str|re.Pattern):
        """
        Add a command handler to the bot

        Usage:
        @bot.command_handler(command="/help")
        async def handle_help_command(message: str, context: BaseContext):
            print(message)
            print(context)
            await context.reply("Help message")
        """
        def wrapper(handler: BaseHandler):
            async def inner(update: Update, context: BaseContext) -> bool:
                if not isinstance(update, UpdateTextMessage):
                    print(f"\033[1;32m wrapper \033[m", command, "Not a text message")
                    return False
                if isinstance(command, str):
                    if update.text.startswith(command):
                        print(f"\033[1;32m wrapper \033[m", command, "Text message starts with command")
                        await handler(update, context)
                        return True
                elif isinstance(command, re.Pattern):
                    if command.match(update.text):
                        print(f"\033[1;32m wrapper \033[m", command, "Text message matches command")
                        await handler(update, context)
                        return True
                print(f"\033[1;32m wrapper \033[m", command, "No match")
                return False
            self._handlers.append(inner)
            return inner
        return wrapper
