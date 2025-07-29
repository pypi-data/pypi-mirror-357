"""
Getting started

This example illustrates the most basic bot functionality.

1. A user connects to the bot
2. The bot sends a hello message to the user
3. The user can then interact with the bot by sending text messages
"""

from python_simplex_bot import Bot
from python_simplex_bot.types import BaseContext


bot = Bot(url="ws://localhost:5225")

@bot.hello_handler
async def hello_handler(context: BaseContext):
    """
    This handler is called when a new user connects to the bot
    """
    await context.reply(f"Hello, {context.username}!\n"
                        f"This is an example bot.\n"
                        f"Type /help to see the available commands.\n"
                        f"Type /square NUMBER to get the square of a number.\n"
                        f"Type anything else to echo your message.")

@bot.command_handler(command="/help")
async def help_handler(message: str, context: BaseContext):
    """
    This handler is called when a user sends a text message that starts with /help
    """
    await context.reply("/help - Show this help message\n"
                        "/square NUMBER - Get the square of a number\n"
                        "Anything else - Echo your message")

@bot.command_handler(command="/square")
async def square_handler(message: str, context: BaseContext):
    """
    This handler is called when a user sends a text message that starts with /square
    """
    command_args = message.split(" ")[1:]
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
async def echo_handler(message: str, context: BaseContext):
    """
    text_handler is called for all text messages
    """
    print(message)
    await context.reply("You said: " + message)

"""
Start the bot
"""
bot.start()