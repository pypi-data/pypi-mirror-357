from typing import Any, Unpack

from aiohttp import ClientSession
from vroid.parameter import (
    RequestAccessTokenParameters,
    RequestToInitiateAuthorizationParameters,
    RevokeAccessTokenParameters,
    VRoidParameters,
)
from vroid.request import VRoidRequest
from vroid.route import Route


class VRoidOAuth(VRoidRequest):
    def __init__(
        self,
        session: ClientSession,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        super().__init__(session)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @classmethod
    async def create(
        cls,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> "VRoidOAuth":
        session = ClientSession()
        instance = cls(session, client_id, client_secret, redirect_uri)
        return instance

    def request_to_initiate_authorization(
        self, **kwargs: Unpack[RequestToInitiateAuthorizationParameters]
    ) -> str:
        parameters = VRoidParameters(
            **{
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                **kwargs,
            }
        )
        route = Route("GET", "/oauth/authorize", query_parameters=parameters)
        return route.paramiterized_url

    async def request_access_token(
        self, **kwargs: Unpack[RequestAccessTokenParameters]
    ) -> str:
        parameters = VRoidParameters(
            **{
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                **kwargs,
            }
        )
        route = Route("POST", "/oauth/token", query_parameters=parameters)
        response = await self.fetch(route)
        return response

    async def revoke_access_token(
        self, **kwargs: Unpack[RevokeAccessTokenParameters]
    ) -> None:
        parameters = VRoidParameters(
            **{
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                **kwargs,
            }
        )
        route = Route("POST", "/oauth/revoke", request_parameters=parameters)
        self.headers.update(
            {
                "Authorization": f"Bearer {kwargs['token']}",
            }
        )
        await self.fetch(route)
        self.headers.pop("Authorization")
        return None

    async def __aenter__(self):
        return await super().__aenter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        return False
