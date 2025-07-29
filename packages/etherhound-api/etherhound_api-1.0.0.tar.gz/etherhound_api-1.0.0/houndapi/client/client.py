from .methods import APIMethods
from aiohttp import ClientSession
from typing import Literal, Any, Dict, List, Union

class HoundAPI(APIMethods):
    '''the API that wraps all of the methods
    
    Args:
      host (str, *optional*): the host/domain ex: myapi.net, 127.0.0.1, default="127.0.0.1"
      port (int, *optional*): the host port, default = None
      protocol (str, *optional*): the host protocol, default = "http"'''

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int | None = None,
        protocol: Literal["http", "https"] = "http"
    ):
        self.session = ClientSession(
            base_url=protocol+f"://{host + str(f':{port}' if port else '')}"
        )
    
    async def get(
        self,
        endpoint: str
    ) -> Union[
        Dict[str, Any],
        List[Dict[str, Any]]
    ]:
        async with self.session.get(
            url=endpoint
        ) as resp:
            return await resp.json()
    
    async def post(
        self,
        endpoint: str,
        body: Dict[str, Any] = None
    ) -> Union[
        Dict[str, Any],
        List[Dict[str, Any]]
    ]:
        async with self.session.post(
            endpoint,
            json=body
        ) as resp:
            return await resp.json()

    async def delete(
        self,
        endpoint: str,
        body: Dict[str, Any] = None
    ) -> Union[
        Dict[str, Any],
        List[Dict[str, Any]]
    ]:
        async with self.session.delete(
            url=endpoint,
            json=body
        ) as resp:
            return await resp.json()
    
    async def close(self) -> None:
        '''Close the aiohttp ClientSession'''
        await self.session.close()