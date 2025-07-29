import json
from pydantic import BaseModel
from typing import Literal
from .datatypes import ComposedMessage

CmdGetUserInfo = lambda:'/u'
CmdCreateAddressIfNotExists = lambda:'/address'
CmdShowAddress = lambda: '/show_address'
CmdAcceptContactRequest = lambda contactReqId: f'/_accept {contactReqId}'
CmdRejectContactRequest = lambda contactReqId: f'/_reject {contactReqId}'
def CmdSendMessage(chatType: Literal['chat', 'group'], chatId: str, messages: list[ComposedMessage]):
    return (
        f"/_send {'@' if chatType == 'chat' else '#'}{chatId} json "
        f"{json.dumps([m.model_dump(exclude_none=True) for m in messages], ensure_ascii=False, separators=(',', ':'))}"
    )

CommandType = Literal[
    '/u',
    '/address',
    '/show_address'
] | str

class Command(BaseModel):
    corrId: str
    cmd: CommandType

