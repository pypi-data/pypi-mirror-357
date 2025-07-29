import asyncio
import time
import uuid
import json
import traceback
from typing import List, Dict, Callable, Optional, Any
from dataclasses import dataclass
import websockets
from python_simplex_bot.websocket_client.commands import (
    CmdGetUserInfo,
    CmdCreateAddressIfNotExists,
    CmdShowAddress
)

"""
Websocket client for the bot
"""

@dataclass
class OutboundMessage:
    corrId: str
    message: str
    createdAt: int

class WebsocketClient:
    def __init__(self,
                 url: str = "ws://localhost:3030",
                 timeout: int = 60,
                 on_message: Callable[[str], None] = None,
                 aio_loop: asyncio.AbstractEventLoop|None = None):
        self.url = url
        self.timeout = timeout
        self.outbound_queue: List[OutboundMessage] = []
        self._last_retry_time: Dict[str, float] = {}
        self.ext_on_message = on_message
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._response_futures: Dict[str, asyncio.Future] = {}
        self._connection_ready = asyncio.Event()
        self._corr_id_counter = 0

    async def _connect(self):
        """Connect to the websocket server and start message handling"""
        self._running = True
        while self._running:
            try:
                async with websockets.connect(self.url) as websocket:
                    self.ws = websocket
                    
                    # Start message handling task
                    message_handler = asyncio.create_task(self._message_handler())
                    
                    # Wait a bit to ensure message handler is running
                    await asyncio.sleep(0.1)
                    
                    # Send initial commands
                    # user_info = await self.cmd(CmdGetUserInfo())
                    
                    address = await self.cmd(CmdCreateAddressIfNotExists())
                    if address['resp']['Left']:
                        address = await self.cmd(CmdShowAddress())
                    print(f"Bot started. Address:\n{address['resp']['Right']['contactLink']['connLinkContact']['connFullLink']}\n")
                    
                    # Wait for message handler to complete
                    await message_handler
                    
            except Exception as e:
                print(f"Runtime error: {e}")
                raise

    async def _message_handler(self):
        """Handle incoming messages"""
        while self._running:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                await self._handle_message(message)
                await self._try_send_queued_messages()
            except asyncio.TimeoutError:
                await self._try_send_queued_messages()
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Message handling error: {e}")
                traceback.print_exc()
                break

    async def _handle_message(self, message: str):
        """Handle incoming messages and resolve response futures"""
        try:
            data = json.loads(message)
            corr_id = data.get("corrId")
            if corr_id and corr_id in self._response_futures:
                future = self._response_futures.pop(corr_id)
                if not future.done():
                    future.set_result(data)
            
            if self.ext_on_message:
                await self.ext_on_message(message)
        except json.JSONDecodeError:
            print(f"JSONDecodeError: {message}")

    async def cmd(self, command: Dict[str, Any], wait_for_response: bool = True) -> Dict[str, Any]:
        """
        Send a command and wait for its response
        
        Args:
            command: Dictionary containing command data with corrId and cmd
            
        Returns:
            Dictionary containing the command response
        """
        if not self.ws:
            raise RuntimeError("WebSocket is not connected")
        
        corr_id = f'{self._corr_id_counter:06d}'
        self._corr_id_counter += 1
            
        # Create a future for this command's response
        future = asyncio.Future()
        self._response_futures[corr_id] = future
        
        # Send the command
        await self.ws.send(json.dumps({
            "corrId": corr_id,
            "cmd": command
        }))
        
        try:
            if wait_for_response:
                # Wait for response with timeout
                response = await asyncio.wait_for(future, timeout=self.timeout)
                return response
            else:
                return None
        except asyncio.TimeoutError:
            self._response_futures.pop(corr_id, None)
            raise TimeoutError(f"Command {corr_id} timed out after {self.timeout} seconds")
        except Exception as e:
            self._response_futures.pop(corr_id, None)
            raise

    async def send(self, message: str) -> str:
        """
        Queue a message for sending and return its correlation ID
        """
        corr_id = str(uuid.uuid4())
        outbound = OutboundMessage(
            corrId=corr_id,
            message=message,
            createdAt=int(time.time() * 1000)
        )
        self.outbound_queue.append(outbound)
        self._last_retry_time[corr_id] = time.time()
        return corr_id

    async def _try_send_queued_messages(self):
        """
        Attempt to send all queued messages
        """
        if not self.ws:
            return

        current_time = time.time()
        messages_to_remove = []

        for msg in self.outbound_queue:
            if current_time - self._last_retry_time[msg.corrId] > self.timeout:
                messages_to_remove.append(msg)
                continue

            try:
                await self.ws.send(msg.message)
                messages_to_remove.append(msg)
            except Exception:
                # If send fails, message stays in queue for next retry
                pass

        # Remove successfully sent or timed out messages
        for msg in messages_to_remove:
            self.outbound_queue.remove(msg)
            self._last_retry_time.pop(msg.corrId, None)

    def _stop(self):
        """Stop the websocket client"""
        self._running = False
        if self.ws:
            asyncio.create_task(self.ws.close())

