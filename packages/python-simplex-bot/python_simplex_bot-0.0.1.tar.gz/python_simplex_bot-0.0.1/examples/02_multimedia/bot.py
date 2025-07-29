"""
This example demonstrates how to send and receive images and audio files.
"""

import os
from simplex_bot import Bot
from simplex_bot.types import UpdateNewContact, UpdateTextMessage, UpdateImageMessage, UpdateAudioMessage, BaseContext


bot = Bot(url="ws://localhost:5225")
cwd = os.path.dirname(os.path.abspath(__file__))


IMAGE_FILE_PATH = os.path.join(cwd, "image.jpg")
AUDIO_FILE_PATH = os.path.join(cwd, "audio.ogg")
COMMAND_DESCRIPTION_TEXT = """*Available commands:*
- `/help` - Show this help
- `/image` - Send an image
- `/audio` - Send an audio
"""


@bot.hello_handler
async def hello_handler(update: UpdateNewContact, context: BaseContext):
    await context.reply(f"Hello, {update.peer.user.username}!\n"
                        f"Send me an image or audio file, or one of the following commands:\n"
                        f"{COMMAND_DESCRIPTION_TEXT}")

@bot.command_handler(command="/help")
async def help_handler(update: UpdateTextMessage, context: BaseContext):
    await context.reply(COMMAND_DESCRIPTION_TEXT)

@bot.image_handler
async def image_handler(update: UpdateImageMessage, context: BaseContext):
    """
    This handler is called when a user sends an image
    """
    await context.reply(f"Image received:\n"
                        f"Temp file location: {update.image.temp_file_location}\n"
                        f"SHA256: {update.image.sha256}\n")

@bot.audio_handler
async def audio_handler(update: UpdateAudioMessage, context: BaseContext):
    """
    This handler is called when a user sends an audio
    """
    await context.reply(f"Audio received:\n"
                        f"File type: {update.audio.file_type}\n"
                        f"Temp file location: {update.audio.temp_file_location}\n"
                        f"SHA256: {update.audio.sha256}\n")

@bot.command_handler(command="/image")
async def image_command_handler(update: UpdateTextMessage, context: BaseContext):
    """
    This handler illustrates how to send an image to the user
    """
    await context.reply("Sending an image...")
    await context.send_image(update.image.temp_file_location)

@bot.command_handler(command="/audio")
async def audio_command_handler(update: UpdateTextMessage, context: BaseContext):
    """
    This handler illustrates how to send an audio to the user
    """
    await context.reply("Sending an audio...")
    await context.send_audio(update.audio.temp_file_location)

bot.start()
