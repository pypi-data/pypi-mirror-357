from .subscribe import Subscribe
from .unsubscribe import Unsubscribe
from .poll import Poll

class APIMethods(
    Subscribe,
    Unsubscribe,
    Poll
):
    pass