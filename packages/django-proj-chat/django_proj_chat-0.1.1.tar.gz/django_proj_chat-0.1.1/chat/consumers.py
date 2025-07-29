import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
        else:
            self.room_name = f'chat_{self.user.id}'
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        recipient_id = data['recipient_id']
        content = data['content']

        # Save message to database
        recipient = await database_sync_to_async(User.objects.get)(id=recipient_id)
        message = await database_sync_to_async(Message.objects.create)(
            sender=self.user,
            recipient=recipient,
            content=content
        )

        # Send message to recipient's group
        await self.channel_layer.group_send(
            f'chat_{recipient_id}',
            {
                'type': 'chat_message',
                'message': {
                    'sender': self.user.username,
                    'content': content,
                    'timestamp': message.timestamp.isoformat()
                }
            }
        )

        # Send message back to sender
        await self.send(text_data=json.dumps({
            'message': {
                'sender': self.user.username,
                'content': content,
                'timestamp': message.timestamp.isoformat()
            }
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))