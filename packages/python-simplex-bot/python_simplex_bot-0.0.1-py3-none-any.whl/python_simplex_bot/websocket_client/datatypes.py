from pydantic import BaseModel
from typing import Any, Literal, Optional, Union

class _Allow(BaseModel):
    allow: Literal['yes', 'no']

class UserPreferences(BaseModel):
    timedMessages: _Allow
    fullDelete: _Allow
    reactions: _Allow
    voice: _Allow
    calls: _Allow

class Profile(BaseModel):
    profileId: Optional[int] = None
    displayName: str
    fullName: str
    localAlias: Optional[str] = None
    image: Optional[str] = None
    preferences: Optional[UserPreferences] = None

class User(BaseModel):
    userId: int
    agentUserId: str
    userContactId: int
    localDisplayName: str
    profile: Profile
    fullPreferences: UserPreferences
    activeUser: bool
    activeOrder: int
    showNtfs: bool
    sendRcptsContacts: bool
    sendRcptsSmallGroups: bool

class activeUser(BaseModel):
    type: Literal['activeUser']
    user: User

class ConnLinkContact(BaseModel):
    connFullLink: str

class ContactLink(BaseModel):
    connLinkContact: ConnLinkContact

class userContactLink(BaseModel):
    type: Literal['userContactLink']
    user: User
    contactLink: ContactLink

class _VersionRange(BaseModel):
    minVersion: int
    maxVersion: int

class ContactRequest(BaseModel):
    contactRequestId: int
    agentInvitationId: str
    userContactLinkId: int
    agentContactConnId: str
    cReqChatVRange: _VersionRange
    localDisplayName: str
    profileId: int
    profile: Profile
    createdAt: str
    updatedAt: str
    xContactId: str
    pqSupport: bool

class receivedContactRequest(BaseModel):
    type: Literal['receivedContactRequest']
    user: User
    contactRequest: ContactRequest

class Connection(BaseModel):
    connId: int
    agentConnId: str
    connChatVersion: int
    peerChatVRange: _VersionRange
    connLevel: int
    viaUserContactLink: int
    viaGroupLink: bool
    connType: str
    connStatus: str
    contactConnInitiated: bool
    localAlias: str
    entityId: int
    pqSupport: bool
    pqEncryption: bool
    authErrCounter: int
    quotaErrCounter: int
    createdAt: str

class ChatSettings(BaseModel):
    enableNtfs: str
    favorite: bool

class _MergedPreferenceEnabled(BaseModel):
    forUser: bool
    forContact: bool

class _UserPreference(BaseModel):
    type: Literal['user']
    preference: _Allow

class _MergedPreference(BaseModel):
    enabled: _MergedPreferenceEnabled
    userPreference: _UserPreference
    contactPreference: _Allow

class MergedPreferences(BaseModel):
    timedMessages: _MergedPreference
    fullDelete: _MergedPreference
    reactions: _MergedPreference
    voice: _MergedPreference
    calls: _MergedPreference

class Contact(BaseModel):
    contactId: int
    localDisplayName: str
    profile: Profile
    activeConn: Connection
    contactUsed: bool
    contactStatus: str
    chatSettings: ChatSettings
    userPreferences: dict[str, Any]
    mergedPreferences: MergedPreferences
    createdAt: str
    updatedAt: str
    chatTs: str
    contactGrpInvSent: bool
    chatTags: list[str]
    chatDeleted: bool

class acceptingContactRequest(BaseModel):
    type: Literal['acceptingContactRequest']
    user: User
    contact: Contact

class contactConnected(BaseModel):
    type: Literal['contactConnected']
    user: User
    contact: Contact

class ChatInfoDirect(BaseModel):
    type: Literal['direct']
    contact: Contact

class ChatInfoGroup(BaseModel):
    type: Literal['group']

class _ChatDir(BaseModel):
    type: Literal['directRcv', 'directSnd']

class ChatItemStatus(BaseModel):
    type: Literal['rcvNew', 'rcvRead', 'sndNew', 'sndSent', 'sndRcvd']
    msgRcptStatus: Optional[str] = None
    sndProgress: Optional[str] = None

class _ChatItemMeta(BaseModel):
    itemId: int
    itemTs: str
    itemText: str
    itemStatus: ChatItemStatus
    sentViaProxy: Optional[bool] = None
    itemSharedMsgId: Optional[str] = None
    itemEdited: bool
    userMention: bool
    deletable: bool
    editable: bool
    createdAt: str
    updatedAt: str

class _E2EEInfo(BaseModel):
    pqEnabled: bool

class _ChatItemContentE2EEInfo(BaseModel):
    type: Literal['rcvDirectE2EEInfo']
    e2eeInfo: _E2EEInfo

class _ChatItemContentChatFeature(BaseModel):
    type: Literal['rcvChatFeature']
    feature: str
    enabled: _MergedPreferenceEnabled

class MCText(BaseModel):
    type: Literal['text']
    text: str

class LinkPreview(BaseModel):
    uri: str
    title: str
    description: str
    image: str

class MCLink(BaseModel):
    type: Literal['link']
    text: str
    preview: LinkPreview

class MCImage(BaseModel):
    type: Literal['image']
    text: str
    image: str  # image preview as base64 encoded data string

class MCFile(BaseModel):
    type: Literal['file']
    text: str

class MCUnknown(BaseModel):
    type: str
    text: str

MsgContent = Union[MCText, MCLink, MCImage, MCFile, MCUnknown]

class _ChatItemContentMsgContent(BaseModel):
    type: Literal['sndMsgContent', 'rcvMsgContent']
    msgContent: MsgContent

class _RcvDirectEvent(BaseModel):
    type: Literal['contactDeleted']

class _ChatItemContentRcvDirectEvent(BaseModel):
    type: Literal['rcvDirectEvent']
    rcvDirectEvent: _RcvDirectEvent

class ChatItem(BaseModel):
    chatDir: _ChatDir
    meta: _ChatItemMeta
    content: Union[_ChatItemContentE2EEInfo,
                   _ChatItemContentChatFeature,
                   _ChatItemContentMsgContent,
                   _ChatItemContentRcvDirectEvent]
    mentions: dict[str, Any]
    reactions: list[str]

class DetailedChatItem(BaseModel):
    chatInfo: Union[ChatInfoDirect, ChatInfoGroup]
    chatItem: ChatItem

class newChatItems(BaseModel):
    type: Literal['newChatItems']
    user: User
    chatItems: list[DetailedChatItem]

class chatItemsStatusesUpdated(BaseModel):
    type: Literal['chatItemsStatusesUpdated']
    user: User
    chatItems: list[DetailedChatItem]

class contactDeletedByContact(BaseModel):
    type: Literal['contactDeletedByContact']
    user: User
    contact: Contact

class _RcvQueue(BaseModel):
    agentConnId: str
    server: str
    agentQueueId: str

class agentRcvQueuesDeleted(BaseModel):
    type: Literal['agentRcvQueuesDeleted']
    deletedRcvQueues: list[_RcvQueue]

class agentConnsDeleted(BaseModel):
    type: Literal['agentConnsDeleted']
    agentConnIds: list[str]

class RcvFileDescr(BaseModel):
    fileDescrId: int
    fileDescrText: str
    fileDescrPartNo: int
    fileDescrComplete: bool

class XftpRcvFile(BaseModel):
    rcvFileDescription: RcvFileDescr
    agentRcvFileDeleted: bool
    userApprovedRelays: bool

class FileInvitation(BaseModel):
    fileName: str
    fileSize: int

class FileStatus(BaseModel):
    type: Literal['new'] | str

class RcvFileTransfer(BaseModel):
    fileId: int
    xftpRcvFile: XftpRcvFile
    fileInvitation: FileInvitation
    fileStatus: FileStatus
    senderDisplayName: str
    chunkSize: int
    cancelled: bool

class rcvFileDescReady(BaseModel):
    type: Literal['rcvFileDescReady']
    user: User
    chatItem: DetailedChatItem
    rcvFileTransfer: RcvFileTransfer
    rcvFileDescr: RcvFileDescr

class ComposedMessage(BaseModel):
    filePath: str|None
    quotedItemId: int|None
    msgContent: MsgContent



class errorDuplicateContactLink(BaseModel):
    type: Literal['errorDuplicateContactLink']

class errorStore(BaseModel):
    type: Literal['errorStore']
    storeError: errorDuplicateContactLink|Any

class chatCmdError(BaseModel):
    type: Literal['chatCmdError']
    chatError: errorStore|Any

class _AgentErrorConnNotFound(BaseModel):
    type: Literal['NOT_FOUND']

class _AgentError(BaseModel):
    type: Literal['CONN']
    connError: _AgentErrorConnNotFound

class errorAgent(BaseModel):
    type: Literal['errorAgent']
    agentError: _AgentError|Any

class chatError(BaseModel):
    type: Literal['chatError']
    chatError: errorAgent|Any
