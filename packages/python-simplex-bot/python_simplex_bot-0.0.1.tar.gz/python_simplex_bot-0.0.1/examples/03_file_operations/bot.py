"""
This example demonstrates how to send and receive files.
"""

import os
from simplex_bot import Bot
from simplex_bot.types import (
    UpdateNewContact,
    UpdateTextMessage,
    UpdateFileMessage,
    BaseContext
)

bot = Bot(url="ws://localhost:5225")
cwd = os.path.dirname(os.path.abspath(__file__))

SAVE_PATH = os.path.join(cwd, "files")
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

COMMAND_DESCRIPTION_TEXT = """Send me a file to store it. After I save it, I'll send you a message with the file ID so the file can be retrieved later.

*Available commands:*
- `/help` - Show this help message
- `/file FILEID` - Retrieve a file by its ID
- `/list` - List all files
"""

@bot.hello_handler
async def hello_handler(update: UpdateNewContact, context: BaseContext):
    await context.reply(f"Hello, {update.peer.user.username}! I'm a simple file storage bot.\n"
                        f"{COMMAND_DESCRIPTION_TEXT}")

@bot.file_handler
async def file_handler(update: UpdateFileMessage, context: BaseContext):
    await context.reply("File received.")

@bot.command_handler(command="/help")
async def help_handler(update: UpdateTextMessage, context: BaseContext):
    await context.reply("Send me a file with the `/file` command.")

@bot.command_handler(command="/file")
async def file_command_handler(update: UpdateTextMessage, context: BaseContext):
    await context.reply("Sending a file...")

@bot.command_handler(command="/list")
async def list_command_handler(update: UpdateTextMessage, context: BaseContext):
    await context.reply("Listing all files...")

bot.start()