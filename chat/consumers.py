from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils.timezone import now
from channels.exceptions import DenyConnection
import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Import model inside the method
        from chat.models import Message

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        if self.scope['user'].is_authenticated:
            self.username = self.scope['user'].username

            # Add to the group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Fetch past messages asynchronously
            past_messages = await sync_to_async(list)(
                Message.objects.filter(room_name=self.room_name).order_by('-timestamp')[:50]
            )

            # Prepare and send past messages
            for message in reversed(past_messages):  # Oldest first
                sender_username = await sync_to_async(lambda: message.sender.username)()
                await self.send(text_data=json.dumps({
                    'message': message.message,
                    'username': sender_username,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                }))

            # Notify user
            await self.send(text_data=json.dumps({
                'message': f"You have entered Room - {self.room_name}"
            }))
        else:
            raise DenyConnection("You must be logged in to join the chat room.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        from chat.models import Message

        if not self.scope['user'].is_authenticated:
            return

        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        # Save message asynchronously
        await self.save_message(message)

        # Broadcast the message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.username,
                'sender_channel_name': self.channel_name
            }
        )

    async def chat_message(self, event):
        # Broadcast the message to others in the group
        if event['sender_channel_name'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'username': event['username']
            }))

    async def save_message(self, message):
        from chat.models import Message
        await sync_to_async(Message.objects.create)(
            room_name=self.room_name,
            sender=self.scope['user'],
            message=message,
            timestamp=now()
        )
