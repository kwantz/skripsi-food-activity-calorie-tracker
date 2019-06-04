from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import fact.routing

application = ProtocolTypeRouter({
    # (http->django temp is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            fact.routing.websocket_urlpatterns
        )
    ),
})