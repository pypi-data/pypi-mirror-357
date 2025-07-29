from pydantic import BaseModel
from typing import Union, List

class SubscriptionResponse(BaseModel):
    ok: bool
    message: Union[str, None]
    result: Union[
        Union[None, bool],
        Union[str, List[str]]
    ]