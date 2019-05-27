from django.conf.urls import url
from django.urls import path
from fact.websockets.online_users import OnlineUsers

websocket_urlpatterns = [
    path("online-users", OnlineUsers)
]