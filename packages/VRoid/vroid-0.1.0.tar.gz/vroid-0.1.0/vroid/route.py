from vroid.parameter import VRoidParameters
from yarl import URL


class Route:
    URL = URL("https://hub.vroid.com")

    def __init__(
        self,
        method: str,
        path: str,
        *,
        query_parameters: VRoidParameters | None = None,
        request_parameters: VRoidParameters | None = None,
    ):
        self.path = path
        self.method = method
        self.query_parameters = {
            k: str(v) for k, v in (query_parameters or {}).items() if v is not None
        }
        self.request_parameters = request_parameters

    @property
    def full_url(self) -> str:
        return self.URL.with_path(self.path).human_repr()

    @property
    def paramiterized_url(self) -> str:
        return (
            self.URL.with_path(self.path).with_query(self.query_parameters).human_repr()
        )
