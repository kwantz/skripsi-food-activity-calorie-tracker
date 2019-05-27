from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

persons = 0

class OnlineUsers(WebsocketConsumer):

    def connect(self):
        global persons

        # Join room group
        add = async_to_sync(self.channel_layer.group_add)
        add("room_group_online", self.channel_name)
        persons += 1

        self.accept()
        send = async_to_sync(self.channel_layer.group_send)
        send("room_group_online", {
            'type': 'message'
        })

    def disconnect(self, close_code):
        global persons

        # Leave room group
        discard = async_to_sync(self.channel_layer.group_discard)
        discard("room_group_online", self.channel_name)

        persons -= 1
        send = async_to_sync(self.channel_layer.group_send)
        send("room_group_online", {
            'type': 'message'
        })

    def message(self, event):
        global persons

        # Send message to WebSocket
        self.send(text_data=str(persons))
