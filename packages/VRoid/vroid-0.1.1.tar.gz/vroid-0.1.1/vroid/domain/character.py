from typing import Literal, TypedDict, NotRequired

from vroid.domain.character_model_verison import CharacterModelVersionSerializer
from vroid.domain.image import (
    FullBodyImageSerializer,
    ImageSerializer,
    PortraitImageSerializer,
)
from vroid.domain.user import UserDetailSerializer, UserSerializer


class CharacterModelLicenseSerializer(TypedDict):
    modification: Literal["default", "disallow", "allow"]
    redistribution: Literal["default", "disallow", "allow"]
    credit: Literal["default", "necessary", "unnecessary"]
    characterization_allowed_user: Literal["default", "author", "everyone"]
    sexual_expression: Literal["default", "disallow", "allow"]
    violent_expression: Literal["default", "disallow", "allow"]
    corporate_commercial_use: Literal["default", "disallow", "allow"]
    personal_commercial_use: Literal["default", "disallow", "profit", "nonprofit"]


class TagSerializer(TypedDict):
    name: str
    locale: str | None
    en_name: str | None
    ja_name: str | None


class AgeLimitSerializer(TypedDict):
    is_r18: bool
    is_r15: bool
    is_adult: bool


class CharacterSerializer(TypedDict):
    user: UserSerializer
    id: str
    name: str
    is_private: bool
    created_at: str
    published_at: str | None


class CharacterModelBoothItemSerializer(TypedDict):
    booth_item_id: int
    part_category: str | None


class CharacterModelSerializer(TypedDict):
    id: str
    name: str | None
    is_private: bool
    is_downloadable: bool
    is_comment_off: bool
    is_other_users_available: bool
    is_other_users_allow_viewer_preview: bool
    is_hearted: bool
    portrait_image: PortraitImageSerializer
    full_body_image: FullBodyImageSerializer
    license: NotRequired[CharacterModelLicenseSerializer]
    created_at: str
    heart_count: int
    download_count: int
    usage_count: int
    view_count: int
    published_at: str | None
    tags: list[TagSerializer]
    age_limit: AgeLimitSerializer
    character: CharacterSerializer
    latest_character_model_version: NotRequired[CharacterModelVersionSerializer]
    character_model_booth_items: list[CharacterModelBoothItemSerializer]


class TextFragmentSerializer(TypedDict):
    type: Literal["plain", "url", "tag"]
    body: str
    normalized_body: str


class MotionSerializer(TypedDict):
    personality_name: str
    name: str
    url: str


class PersonalitySerializer(TypedDict):
    name: str
    label: str
    label_en: str
    waiting_motion: MotionSerializer
    appearing_motion: MotionSerializer
    liked_motion: MotionSerializer
    other_motions: list[MotionSerializer]


class CharacterWebsiteSerializer(TypedDict):
    id: str
    url: str
    service: str


class CharacterHeaderSerializer(TypedDict):
    original: ImageSerializer


class CharacterIconSerializer(TypedDict):
    is_default_image: bool
    original: ImageSerializer


class CharacterDetailSerializer(TypedDict):
    character: CharacterSerializer
    user_detail: UserDetailSerializer
    description_fragments: list[TextFragmentSerializer]
    websites: list[CharacterWebsiteSerializer]
    header: CharacterHeaderSerializer
    icon: CharacterIconSerializer
    description: str


class CharacterModelDetailSerializer(TypedDict):
    character_model: CharacterModelSerializer
    description_fragments: list[TextFragmentSerializer]
    reply_count: int
    status_id: str
    description: str
    ogp_image_url: str
    personality: PersonalitySerializer
    character_detail: CharacterDetailSerializer
