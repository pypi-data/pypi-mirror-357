from enum import Enum
from typing import List, Optional
from datetime import datetime

class CloudhandsPurchaseResult:
    def __init__(self, is_successful: bool, errors: list, transaction_id: str = None):
        self.is_successful = is_successful
        self.errors = errors
        self.transaction_id = transaction_id

class TransactionState(Enum):
    Pending = 0
    Complete = 1
    Failed = 2

class ChargeType(Enum):
    Each = "Each"
    Monthly = "Monthly"
    Variable = "Variable"

class CloudhandsTransaction:
    def __init__(self, author_id: str, user_id: str, amount: int = None, type: str = None, 
                 date: str = None, description: str = None, processed: str = None, 
                 process_state: TransactionState = None):
        self.author_id = author_id
        self.user_id = user_id
        self.amount = amount
        self.type = type
        self.date = date
        self.description = description
        self.processed = processed
        self.process_state = process_state

class PostType(Enum):
    Post = "Post"
    News = "News"
    Tool = "Tool"
    Article = "Article"

class MessageType(Enum):
    Text = "Text"
    Html = "Html"
    Markdown = "Markdown"

class ContentWarning(Enum):
    NoneWarning = "None"
    Suggestive = "Suggestive"
    Nudity = "Nudity"
    Porn = "Porn"

class LanguageTypes(Enum):
    English = "English"

class WhoCanReply(Enum):
    Everybody = "Everybody"
    Nobody = "Nobody"
    Mentioned = "Mentioned"
    Followed = "Followed"

class PostVisibility(Enum):
    Everybody = "Everybody"
    Private = "Private"

class BrandAffiliate(Enum):
    NoneAffiliate = "None"
    Affiliate = "Affiliate"

class CloudhandsPost:
    def __init__(
        self,
        postId: Optional[str] = None,
        userId: Optional[str] = None,
        postType: PostType = PostType.Post,
        messageType: MessageType = MessageType.Text,
        title: Optional[str] = None,
        message: Optional[str] = None,
        warning: ContentWarning = ContentWarning.NoneWarning,
        images: Optional[List[dict]] = None,
        languages: Optional[List[LanguageTypes]] = None,
        whoCanReply: WhoCanReply = WhoCanReply.Everybody,
        userName: Optional[str] = None,
        avatar: Optional[str] = None,
        toolRefs: Optional[List[int]] = None,
        tagged: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        publishDateTime: Optional[datetime] = None,
        postVisibility: PostVisibility = PostVisibility.Everybody,
        brandAffiliate: BrandAffiliate = BrandAffiliate.NoneAffiliate,
        originalPost: Optional[str] = None,
        numLikes: int = 0,
        userLike: bool = False,
        userSave: bool = False,
        isFollowed: bool = False,
        comments: Optional[List[str]] = None,
        numComments: int = 0,
        tools: Optional[List[dict]] = None,
        id: Optional[int] = None,
        created: Optional[datetime] = None,
        updated: Optional[datetime] = None,
    ):
        self.postId = postId
        self.userId = userId
        self.postType = postType
        self.messageType = messageType
        self.title = title
        self.message = message
        self.warning = warning
        self.images = images or []
        self.languages = languages or [LanguageTypes.English]
        self.tagged = tagged or []
        self.whoCanReply = whoCanReply
        self.userName = userName
        self.avatar = avatar
        self.toolrefs = toolRefs or []
        self.tags = tags or []
        self.publishDateTime = publishDateTime or datetime.utcnow()
        self.postVisibility = postVisibility
        self.brandAffiliate = map_to_enum(brandAffiliate, BrandAffiliate)
        self.originalPost = originalPost
        self.numLikes = numLikes
        self.userLike = userLike
        self.userSave = userSave
        self.isFollowed = isFollowed
        self.comments = comments or []
        self.numComments = numComments
        self.tools = tools or []
        self.id = id
        self.created = created or datetime.utcnow()
        self.updated = updated or datetime.utcnow()

    def __str__(self):
        return f"CloudhandsPost({self.__dict__})"

class CloudhandsPostRequest:
    def __init__(
            self, 
            title: Optional[str] = None, 
            message: Optional[str] = None,
            images: Optional[List[dict]] = [],
        ):
            #self.postId = postId,
            # get string value of the enum
            self.postType = PostType.Post.value 
            self.messageType = MessageType.Text.value
            self.title = title
            self.message = message
            self.warning = ContentWarning.NoneWarning.value
            self.images = images
            self.whoCanReply = WhoCanReply.Everybody.value
            self.toolRefs = []
            self.publishDateTime = datetime.utcnow().isoformat()
            self.postVisibility = PostVisibility.Everybody.value
            self.brandAffiliate = BrandAffiliate.NoneAffiliate.value
    
    def __str__(self):
        return f"CloudhandsPostBody({self.__dict__})"

def map_to_enum(value, enum_class):
    """
    Maps a value to the corresponding enum, handling special cases for `None`.

    :param value: The value to map.
    :param enum_class: The enum class to map to.
    :return: The corresponding enum value.
    """
    # if value is none or the string 'None', return the None enum value
    if value is None or value == 'None':
        if enum_class == ContentWarning:
            return ContentWarning.NoneWarning
        elif enum_class == BrandAffiliate:
            return BrandAffiliate.NoneAffiliate
    return enum_class(value)


