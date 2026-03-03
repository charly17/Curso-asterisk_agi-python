import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ami_app.ami import AMIAsterisk


class WebsocketConsumer(AsyncWebsocketConsumer):
    groups = ["broadcast"]

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("ami_socket", self.channel_name)
        await self.send('{"msg": "connected"}')

    async def receive(self, text_data=None, bytes_data=None):
        if text_data == 'IAXPeers':
            AMIAsterisk().get_iax_peers()

    async def disconnect(self, close_code):
        pass

    async def send_message(self, message):
        await self.send(text_data=json.dumps(message['message']))
