from typing import TYPE_CHECKING, Any
from .peer import Peer
if TYPE_CHECKING:
    from python_simplex_bot import Bot


class BaseContext:
    _bot: 'Bot'
    recipient: Peer
    username: str|None = None
    group: str|None = None
    args: dict[str, Any] = {}

    def __init__(self, bot: 'Bot', recipient: Peer, **kwargs):
        self._bot = bot
        self.recipient = recipient
        self.args = {key: value for key, value in kwargs.items() if key not in ["recipient"]}
    
    async def reply(self, message: str):
        await self._bot.send_text(message, self.recipient)
