from typing import Any, Optional

from aiohttp import ClientSession
from vroid.exception import VRoidException
from vroid.route import Route


class VRoidRequest:
    X_API_VERSION = 11

    def __init__(self, session: Optional[ClientSession] = None):
        self.session = session
        self.headers = {
            "X-Api-Version": str(self.X_API_VERSION),
        }

    async def fetch(self, route: Route) -> Any:
        if not self.session:
            self.session = ClientSession()

        async with self.session.request(
            route.method,
            route.full_url,
            params=route.query_parameters,
            data=route.request_parameters,
            headers=self.headers,
        ) as response:
            if response.status != 200:
                raise VRoidException(
                    f"Request failed with status {response.status}: {await response.json()}"
                )

            return await response.json()

    async def close(self):
        if self.session:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self.close()
        return False
