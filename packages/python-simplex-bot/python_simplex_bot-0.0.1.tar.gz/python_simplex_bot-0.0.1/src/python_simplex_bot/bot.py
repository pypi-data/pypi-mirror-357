import asyncio
import signal
from python_simplex_bot.handlers import MessageHandlersTrait
from python_simplex_bot.types import BaseContext, Peer, UpdateNewContact, UpdateTextMessage
from python_simplex_bot.types.update import parse_updates
from python_simplex_bot.helpers.autorun import AutorunTrait
from python_simplex_bot.websocket_client.client import WebsocketClient
from python_simplex_bot.websocket_client.commands import (
    CmdAcceptContactRequest,
    CmdSendMessage,
    ComposedMessage
)
from python_simplex_bot.websocket_client.responses import (
    SimplexChatResponse,
    LeftResponse,
    RightResponse,
    receivedContactRequest,
    newChatItems
)
from python_simplex_bot.websocket_client.datatypes import MCText

class Bot(
    WebsocketClient,
    MessageHandlersTrait,
    AutorunTrait
):
    __debug: bool = False
    def __init__(self,
                 url: str = "ws://localhost:5225",
                 aio_loop: asyncio.AbstractEventLoop|None = None,
                 simplex_chat_client_path: str = "simplex-chat",
                 simplex_chat_database_name: str = "simplex-bot-database",
                 debug: bool = False):
        super().__init__(url,
                         on_message=self._on_message,
                         aio_loop=aio_loop)
        self._set_simplex_chat_client_params(url,
                                             simplex_chat_client_path,
                                             simplex_chat_database_name)
        self.__debug = debug
    async def _on_message(self, raw_message: str):
        if self.__debug:
            print(f"Received message: {raw_message}")
        try:
            message = SimplexChatResponse.model_validate_json(json_data=raw_message)
            if isinstance(message.resp, LeftResponse):
                pass
            elif isinstance(message.resp, RightResponse):
                if isinstance(message.resp.Right, receivedContactRequest):
                    await self.cmd(
                        CmdAcceptContactRequest(
                            message.resp.Right.contactRequest.contactRequestId
                        ),
                        wait_for_response=False
                    )
                    # update = UpdateNewContact(message)
        except Exception as e:
            print(f"Error parsing message: {e}")
            return
        for update in parse_updates(message):
            context = BaseContext(bot=self, recipient=update.peer if update else None)
            await self._handle(update, context)
    
    async def send_text(self, message: str, peer: Peer):
        if self.__debug:
            print(f"Sending text to {peer}: {message}")
        await self.cmd(CmdSendMessage(
            chatType='chat',
            chatId=peer.user.id,
            messages=[ComposedMessage(
                filePath=None,
                quotedItemId=None,
                msgContent=MCText(
                    type='text',
                    text=message
                )
            )],
        ), wait_for_response=False)
    
    async def send_image(self, image_url: str, recipient: str, caption: str|None = None):
        pass

    async def send_video(self, video_url: str, recipient: str, caption: str|None = None):
        pass
    
    async def send_audio(self, audio_url: str, recipient: str, caption: str|None = None):
        pass

    async def shutdown(self, signal: signal.Signals, loop: asyncio.AbstractEventLoop):
        print(f"Received {signal.name} signal. Shutting down...")
        print(f"\nReceived exit signal {signal.name}...")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        print(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        self._stop()
        loop.stop()

    async def start_async(self):
        print("Starting bot...")
        loop = asyncio.get_running_loop()

        # Set up signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(s, loop))
            )
        try:
            await super()._connect()
        except asyncio.exceptions.CancelledError as e:
            print("Bot stopped.")
    
    def start(self):
        asyncio.run(self.start_async())