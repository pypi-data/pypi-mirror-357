from typing import TYPE_CHECKING, TypedDict

from vroid.domain.image import ImageSerializer

if TYPE_CHECKING:
    from vroid.domain.character import TextFragmentSerializer


class UserIconSerializer(TypedDict):
    is_default_image: bool
    sq170: ImageSerializer
    sq50: ImageSerializer


class UserSerializer(TypedDict):
    id: str
    pixiv_user_id: str
    name: str
    icon: UserIconSerializer


class UserRelationshipSerializer(TypedDict):
    user_id: str
    is_following: bool
    is_followed: bool


class UserDetailSerializer(TypedDict):
    user: UserSerializer
    description: str
    description_fragments: list["TextFragmentSerializer"]
    following_count: int
    follower_count: int
    relationShip: UserRelationshipSerializer


class AgeLimitSerializer(TypedDict):
    is_r18: bool
    is_r15: bool
    is_adult: bool


class CurrentUserSerializer(TypedDict):
    locale: str
    account_sub_avatar_id: str
    is_pixiv_status_complete: bool
    is_showable_on_pixiv: bool
    is_developer: bool
    is_user_privacy_policy_accepted: bool
    user_detail: UserDetailSerializer
    age_limit: AgeLimitSerializer
