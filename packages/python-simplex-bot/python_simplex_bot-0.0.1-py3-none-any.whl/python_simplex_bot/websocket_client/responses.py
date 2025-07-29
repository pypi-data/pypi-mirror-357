from pydantic import BaseModel
from typing import Any, Union, Optional, TypeVar
from .datatypes import (
    activeUser,
    userContactLink,
    receivedContactRequest,
    acceptingContactRequest,
    contactConnected,
    newChatItems,
    rcvFileDescReady,
    chatItemsStatusesUpdated,
    contactDeletedByContact,
    agentRcvQueuesDeleted,
    agentConnsDeleted,
    chatCmdError,
    chatError
)

T = TypeVar('T', bound=BaseModel)

class LeftResponse(BaseModel):
    Left: Union[chatCmdError, chatError]
    Right: None = None

class RightResponse(BaseModel):
    Left: None = None
    Right: Union[activeUser,
                 userContactLink,
                 receivedContactRequest,
                 acceptingContactRequest,
                 contactConnected,
                 newChatItems,
                 rcvFileDescReady,
                 chatItemsStatusesUpdated,
                 contactDeletedByContact,
                 agentRcvQueuesDeleted,
                 agentConnsDeleted]

class SimplexChatResponse(BaseModel):
    corrId: Optional[str] = None
    resp: Union[LeftResponse, RightResponse]

class TypedLeftResponse[T: BaseModel](BaseModel):
    Left: T
    Right: None = None

class TypedRightResponse[T: BaseModel](BaseModel):
    Left: None = None
    Right: T

class TypedSimplexChatResponse[T: BaseModel](BaseModel):
    corrId: Optional[str] = None
    resp: TypedLeftResponse[T] | TypedRightResponse[T]
