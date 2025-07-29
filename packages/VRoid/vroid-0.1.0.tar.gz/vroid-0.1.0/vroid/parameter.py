from typing import Literal, NotRequired, TypedDict

ALLOW_DISALLOW = Literal["default", "disallow", "allow"]


class VRoidParameters(TypedDict): ...


class CountParameters(VRoidParameters):
    count: NotRequired[int]


class ListParameters(CountParameters):
    max_id: NotRequired[str]


class CategoryParameters(VRoidParameters):
    is_downloadable: NotRequired[bool]
    characterization_allowed_user: NotRequired[Literal["default", "author", "everyone"]]
    violent_expression: NotRequired[ALLOW_DISALLOW]
    sexual_expression: NotRequired[ALLOW_DISALLOW]
    corporate_commercial_use: NotRequired[ALLOW_DISALLOW]
    personal_commercial_use: NotRequired[ALLOW_DISALLOW]
    political_or_religious_usage: NotRequired[ALLOW_DISALLOW]
    antisocial_or_hate_usage: NotRequired[ALLOW_DISALLOW]
    modification: NotRequired[Literal["default", "disallow", "allow_modification"]]
    redistribution: NotRequired[ALLOW_DISALLOW]
    credit: NotRequired[Literal["default", "necessary", "unnecessary"]]
    has_booth_items: NotRequired[bool]
    booth_part_categories: NotRequired[list[str]]


class ListOfCharacterModelsPostedByTheUserParameters(ListParameters):
    publication: NotRequired[str]


class ListOfAvailableCharacterModelsLikedByTheUserParameters(
    ListParameters, CategoryParameters
):
    application_id: str


class ListOfCharacterModelsRecommendedByVRoidHubStaffParameters(ListParameters): ...


class SearchCharacterModelsParameters(CountParameters, CategoryParameters):
    keyword: str
    search_after: NotRequired[str]
    sort: NotRequired[str]


class RequestToInitiateAuthorizationParameters(VRoidParameters):
    response_type: str
    scope: str


class RequestAccessTokenParameters(VRoidParameters):
    grant_type: str
    code: str
    refresh_token: NotRequired[str]


class RevokeAccessTokenParameters(VRoidParameters):
    token: str
