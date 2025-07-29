from houndapi.schema.subscription import (
    LogsSubscription,
    PendingTransactionsSubscription,
)
from houndapi.schema.responses.subscription import (
    SubscriptionResponse
)
from houndapi.logger import get_logger
from typing import Union, List
import houndapi

class Subscribe:

    async def subscribe(
        self: "houndapi.HoundAPI",
        subscriptions: Union[
            Union[LogsSubscription, PendingTransactionsSubscription],
            List[Union[LogsSubscription, PendingTransactionsSubscription]]
        ]
    ) -> Union[SubscriptionResponse, None]:
        '''Subscribe
        
        Args:
          subscriptions (Union[Union[LogsSubscription, PendingTransactionsSubscription],List[Union[LogsSubscription, PendingTransactionsSubscription]]]]): the Subscriptions
        Returns:
          Union[None, :class:`houndapi.schema.responses.subscription.SubscriptionResponse`]'''

        if not isinstance(subscriptions, list): subscriptions = [subscriptions]

        try:
            result = await self.post(
                endpoint="/api/subscribe",
                body=[sub.model_dump() for sub in subscriptions]
            )
            return SubscriptionResponse(
                **result
            )
        except Exception as e:
            get_logger().info(
                f"Failed to subscribe ({e})",
                extra={"endpoint": "/api/subscribe"}
            )