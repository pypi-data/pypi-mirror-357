__app_name__ = "agenticmem"
__version__ = "0.1.1"


from agenticmem.client import AgenticMemClient
from agenticmem_commons.api_schema.service_schemas import (
    UserActionType,
    ProfileTimeToLive,
    InteractionRequest,
    Interaction,
    UserProfile,
    PublishUserInteractionRequest,
    PublishUserInteractionResponse,
    DeleteUserProfileRequest,
    DeleteUserProfileResponse,
    DeleteUserInteractionRequest,
    DeleteUserInteractionResponse,
)
from agenticmem_commons.api_schema.retriever_schema import (
    SearchInteractionRequest,
    SearchUserProfileRequest,
    SearchInteractionResponse,
    SearchUserProfileResponse,
)

debug = False
log = None  # Set to either 'debug' or 'info', controls console logging


__all__ = [
    "AgenticMemClient",
    "UserActionType",
    "ProfileTimeToLive",
    "InteractionRequest",
    "Interaction",
    "UserProfile",
    "PublishUserInteractionRequest",
    "PublishUserInteractionResponse",
    "DeleteUserProfileRequest",
    "DeleteUserProfileResponse",
    "DeleteUserInteractionRequest",
    "DeleteUserInteractionResponse",
    "SearchInteractionRequest",
    "SearchUserProfileRequest",
    "SearchInteractionResponse",
    "SearchUserProfileResponse",
]
