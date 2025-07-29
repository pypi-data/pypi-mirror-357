from houndapi.schema.responses.subscription import (
    SubscriptionResponse
)
from houndapi.logger import get_logger
from typing import Union, List
import houndapi

class Unsubscribe:

    async def unsubscribe(
        self: "houndapi.HoundAPI",
        subscription_id: str,
    ) -> Union[SubscriptionResponse, None]:
        '''Unsubscribe
        
        Args:
          subscription_id (str): the subscription id
        Returns:
          Union[None, :class:`houndapi.schema.responses.subscription.SubscriptionResponse`]'''
        
        try:
            res = await self.delete(
                endpoint=f"/api/unsubscribe/{subscription_id}",
            )
            return SubscriptionResponse(
                **res
            )
        except Exception as e:
            get_logger().info(
                f"Failed to Unsubscribe ({e})",
                extra={"endpoint": f"/api/unsubscribe/{subscription_id}"}
            )