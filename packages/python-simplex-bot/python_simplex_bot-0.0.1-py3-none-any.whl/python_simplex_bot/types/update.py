import time
from typing import Optional
from python_simplex_bot.helpers.formatting import strip_formatting
from .peer import Peer, User, Group
from python_simplex_bot.websocket_client.responses import SimplexChatResponse, TypedSimplexChatResponse
from python_simplex_bot.websocket_client.datatypes import (
    contactConnected,
    newChatItems,
    MCText,
    MCImage,
    MCFile,
    MCUnknown
)


class BaseUpdate:
    peer: Peer
    timestamp: int
    raw_message: SimplexChatResponse

    def __init__(self, raw_message: SimplexChatResponse):
        self.raw_message = raw_message
        self.timestamp = time.time()


class UpdateNewContact(BaseUpdate):
    """
    New contact
    """

    def __init__(self, raw_message: TypedSimplexChatResponse[contactConnected]):
        super().__init__(raw_message)
        self.peer = Peer(
            user=User(
                id=raw_message.resp.Right.contact.contactId,
                username=raw_message.resp.Right.contact.profile.displayName
            ),
            group=None
        )


class UpdateChatFeature(BaseUpdate):
    """
    Chat feature
    """
    feature: str
    enabledForUser: bool
    enabledForContact: bool

    def __init__(self, raw_message: TypedSimplexChatResponse[newChatItems], chat_item_index: int = 0):
        super().__init__(raw_message)
        user=User(
            id=raw_message.resp.Right.chatItems[chat_item_index].chatInfo.contact.contactId,
            username=raw_message.resp.Right.chatItems[chat_item_index].chatInfo.contact.profile.displayName
        )
        self.peer = Peer(
            user=user,
            group=None
        )
        _rcvChatFeature = raw_message.resp.Right.chatItems[chat_item_index].chatItem.content
        self.feature = _rcvChatFeature.feature
        self.enabledForUser = _rcvChatFeature.enabled.forUser
        self.enabledForContact = _rcvChatFeature.enabled.forContact


class UpdateTextMessage(BaseUpdate):
    """
    Text message
    """
    formatted_text: str
    text: str

    def __init__(self, raw_message: TypedSimplexChatResponse[newChatItems], chat_item_index: int = 0):
        super().__init__(raw_message)
        user=User(
            id=raw_message.resp.Right.chatItems[chat_item_index].chatInfo.contact.contactId,
            username=raw_message.resp.Right.chatItems[chat_item_index].chatInfo.contact.profile.displayName
        )
        self.peer = Peer(
            user=user,
            group=None
        )
        self.formatted_text = raw_message.resp.Right.chatItems[chat_item_index].chatItem.content.msgContent.text
        self.text = strip_formatting(self.formatted_text)


class UpdateImageMessage(BaseUpdate):
    """
    Image message
    """
    image_url: str
    formatted_caption: str
    caption: str

    def __init__(self, raw_message: TypedSimplexChatResponse[MCImage]):
        super().__init__(raw_message)
        assert isinstance(raw_message.resp.Right, MCImage)
        self.image_url = raw_message.resp.Right.msgContent.image
        self.formatted_caption = raw_message.resp.Right.msgContent.text
        self.caption = strip_formatting(raw_message.resp.Right.msgContent.text)


class UpdateVideoMessage(BaseUpdate):
    """
    Video message
    """
    video_url: str
    formatted_caption: str
    caption: str

    def __init__(self, raw_message: str):
        super().__init__(raw_message)
        self.video_url = raw_message.split(" ")[1]
        self.formatted_caption = raw_message.split(" ")[2]
        self.caption = strip_formatting(raw_message.split(" ")[2])


class UpdateAudioMessage(BaseUpdate):
    """
    Audio message
    """
    audio_url: str
    formatted_caption: str
    caption: str

    def __init__(self, raw_message: str):
        super().__init__(raw_message)
        self.audio_url = raw_message.split(" ")[1]
        self.formatted_caption = raw_message.split(" ")[2]
        self.caption = strip_formatting(raw_message.split(" ")[2])


Update = (
    UpdateTextMessage |
    UpdateImageMessage |
    UpdateVideoMessage |
    UpdateAudioMessage |
    UpdateChatFeature |
    UpdateNewContact
    )


def parse_updates(raw_response: SimplexChatResponse) -> list[Update]:
    updates = []
    try:
        if raw_response.resp.Right is None:
            return []
        elif raw_response.resp.Right.type == "newChatItems":
            for i, chat_item in enumerate(raw_response.resp.Right.chatItems):
                if chat_item.chatItem.content.type == "rcvChatFeature":
                    updates.append(UpdateChatFeature(raw_response, chat_item_index=i))
                elif chat_item.chatItem.content.type == "rcvMsgContent":
                    content = chat_item.chatItem.content.msgContent
                    if content.type == "text":
                        updates.append(UpdateTextMessage(raw_response, chat_item_index=i))
                    elif content.type == "image":
                        updates.append(UpdateImageMessage(raw_response, chat_item_index=i))
        elif raw_response.resp.Right.type == "contactConnected":
            updates.append(UpdateNewContact(raw_response))
    except Exception as e:
        print(f"Error parsing updates: {e}")
        return []
    return updates
