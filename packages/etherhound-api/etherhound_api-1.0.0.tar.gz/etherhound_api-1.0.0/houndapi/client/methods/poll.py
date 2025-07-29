from houndapi.schema.context import (
    Context
)
from houndapi.logger import get_logger
from typing import Union, List
import houndapi

class Poll:

    async def poll(
        self: "houndapi.HoundAPI",
        subscription_id: str,
        limit: int = 50
    ) -> Union[List[Context], None]:
        '''Poll Subscription Events
        
        Arg:
          subscription_id (str): the subscription id
          limit (int, *optional*): the limit of polled events default=50
        Returns:
          Union[None, List[:class:`houndapi.schema.context.Context`]]'''
        
        try:
            res = await self.get(
                endpoint=f"/api/poll/{subscription_id}?limit={limit}"
            )
            return [
                Context(
                    **r
                ) for r in res
            ]
        except Exception as e:
            get_logger().info(
                f"Failed to Poll Events for subscription ({e})",
                extra={"endpoint": f"/api/poll/{subscription_id}"}
            )