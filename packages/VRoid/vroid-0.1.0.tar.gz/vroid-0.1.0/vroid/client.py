from typing import Any, Unpack

from aiohttp import ClientSession
from vroid.domain.character import CharacterModelSerializer
from vroid.domain.user import CurrentUserSerializer
from vroid.parameter import (
    ListOfAvailableCharacterModelsLikedByTheUserParameters,
    ListOfCharacterModelsPostedByTheUserParameters,
    ListOfCharacterModelsRecommendedByVRoidHubStaffParameters,
)
from vroid.request import VRoidRequest
from vroid.route import Route


class VRoid(VRoidRequest):
    def __init__(self, token: str, session: ClientSession | None = None):
        super().__init__(session=session)
        self.token = token
        self.headers["Authorization"] = f"Bearer {self.token}"

    async def list_of_character_models_posted_by_the_user(
        self, **kwargs: Unpack[ListOfCharacterModelsPostedByTheUserParameters]
    ) -> list[CharacterModelSerializer]:
        route = Route(
            "GET",
            "/api/account/character_models",
            query_parameters=kwargs,
        )

        response = await self.fetch(route)
        return [CharacterModelSerializer(**item) for item in response.get("data", [])]

    async def list_of_available_character_models_liked_by_the_user(
        self, **kwargs: Unpack[ListOfAvailableCharacterModelsLikedByTheUserParameters]
    ) -> list[CharacterModelSerializer]:
        route = Route(
            "GET",
            "/api/account/character_models/liked",
            query_parameters=kwargs,
        )

        response = await self.fetch(route)
        return [CharacterModelSerializer(**item) for item in response.get("data", [])]

    async def list_of_character_models_recommended_by_vroid_Hub_staff(
        self,
        **kwargs: Unpack[ListOfCharacterModelsRecommendedByVRoidHubStaffParameters],
    ) -> list[CharacterModelSerializer]:
        route = Route(
            "GET",
            "/api/account/character_models/recommended",
            query_parameters=kwargs,
        )

        response = await self.fetch(route)
        return [CharacterModelSerializer(**item) for item in response.get("data", [])]

    async def detailed_information_of_a_character_model(
        self, id: str
    ) -> CharacterModelSerializer:
        route = Route(
            "GET",
            f"/api/account/character_models/{id}",
        )

        response = await self.fetch(route)
        return CharacterModelSerializer(**response.get("data", {}))

    async def account_information_for_logged_in_user(self) -> CurrentUserSerializer:
        route = Route(
            "GET",
            "/api/account",
        )

        response = await self.fetch(route)
        return CurrentUserSerializer(**response.get("data", {}))

    async def __aenter__(self) -> "VRoid":
        return await super().__aenter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self.close()
        return False
