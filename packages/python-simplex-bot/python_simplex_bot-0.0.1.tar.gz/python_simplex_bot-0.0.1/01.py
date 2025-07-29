"""
Getting started

This example illustrates the most basic bot functionality.

1. A user connects to the bot
2. The bot sends a hello message to the user
3. The user can then interact with the bot by sending text messages
"""

from python_simplex_bot import Bot
from python_simplex_bot.types import BaseContext, UpdateNewContact, UpdateTextMessage

bot = Bot(url="ws://localhost:5225")

AVAILABLE_COMMANDS_DESCRIPTION = """
*Available commands:*
- `/help` - Show this help message
- `/square NUMBER` - Get the square of a number
- Anything else - Echo your message
"""

@bot.hello_handler
async def hello_handler(update: UpdateNewContact, context: BaseContext):
    """
    This handler is called when a new user connects to the bot
    """
    print("\033[1;31m hello_handler \033[m")
    await context.reply(f"Hello, {update.peer.user.username}! I'm an example bot.\n"
                        f"{AVAILABLE_COMMANDS_DESCRIPTION}")

@bot.command_handler(command="/help")
async def help_handler(update: UpdateTextMessage, context: BaseContext):
    """
    This handler is called when a user sends a text message that starts with /help
    """
    await context.reply(AVAILABLE_COMMANDS_DESCRIPTION)

@bot.command_handler(command="/square")
async def square_handler(update: UpdateTextMessage, context: BaseContext):
    """
    This handler is called when a user sends a text message that starts with /square
    """
    command_args = update.text.split(" ")[1:]
    if len(command_args) == 0:
        await context.reply("Please provide a number to square")
        return
    number = command_args[0]
    try:
        number = float(number)
    except ValueError:
        await context.reply("Please provide a valid number to square")
        return
    await context.reply(f"The square of {number} is {number ** 2}")


@bot.text_handler
async def echo_handler(update: UpdateTextMessage, context: BaseContext):
    """
    text_handler is called for all text messages
    """
    print(update.text)
    await context.reply("You said: " + update.text)

bot.start()
