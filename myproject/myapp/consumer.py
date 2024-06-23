import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import PrivateRoomConnection, PrivateChatRoom
from django.db.models import Count
from django.contrib.auth.models import User
import uuid

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = 'group-chat'
        await self.channel_layer.group_add(
            self.roomGroupName,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                'type': 'chat_message',
                'message': f"{self.scope['user'].username} has connected.",
                'username': 'System',
                'time' : '',
                'message_id': str(uuid.uuid4())
                
            }
        )

    async def disconnect(self, close_code):

        await self.channel_layer.group_send(
            self.roomGroupName,
            {
                'type': 'chat_message',
                'message': f"{self.scope['user'].username} has disconnected.",
                'username': 'System',
                'time' : '',
                'message_id': str(uuid.uuid4())
            }
        )


        await self.channel_layer.group_discard(

            self.roomGroupName,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']


        if message_type == 'chat_message':
            message = text_data_json['message']
            username = text_data_json['username']
            time = text_data_json['time']
            message_id = str(uuid.uuid4())

            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'time': time,
                    'message_id' : message_id
                }
            )
        elif message_type == 'typing':
            username = text_data_json['username']
            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    'type': 'typing',
                    'username': username
                }
            )
        elif message_type == 'stop_typing':
            username = text_data_json['username']
            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    'type': 'stop_typing',
                    'username': username
                }
            )
        elif message_type == 'file_message':
            file_name = text_data_json['file_name']
            file_url = text_data_json['file_url']
            username = text_data_json['username']
            message_id = str(uuid.uuid4())

            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    'type': 'file_message',
                    'file_name': file_name,
                    'file_url': file_url,
                    'username': username,
                    'message_id': message_id
                }
            )

        elif message_type == 'reaction':
            reaction = text_data_json['reaction']
            message_id = text_data_json['message_id']
            username = text_data_json['username']

            await self.channel_layer.group_send(
                self.roomGroupName,
                {
                    'type': 'reaction',
                    'reaction': reaction,
                    'message_id': message_id,
                    'username': username
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        time = event['time']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'time': time,
            'message_id': message_id
        }))

    async def typing(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': username
        }))

    async def stop_typing(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'stop_typing',
            'username': username
        }))

    async def file_message(self, event):
        file_name = event['file_name']
        file_url = event['file_url']
        username = event['username']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'type': 'file_message',
            'file_name': file_name,
            'file_url': file_url,
            'username': username,
            'message_id': message_id
        }))

    async def reaction(self, event):
        reaction = event['reaction']
        message_id = event['message_id']
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'reaction': reaction,
            'message_id': message_id,
            'username': username
        }))




class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        self.room_name = await self.find_or_create_room(self.user)

        room, created = await database_sync_to_async(PrivateChatRoom.objects.get_or_create)(name=self.room_name)

        connection_count = await database_sync_to_async(PrivateRoomConnection.objects.filter(room=room).count)()

        if connection_count >= 2:
            await self.close()
        else:
            await self.add_connection(room, self.user)
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': f"{self.scope['user'].username} has connected.",
                'username': 'System',
                'time' : '',
                'message_id': str(uuid.uuid4())
                
            }
        )

    async def disconnect(self, close_code):

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': f"{self.scope['user'].username} has disconnected.",
                'username': 'System',
                'time' : '',
                'message_id': str(uuid.uuid4())
            }
        )

        await self.remove_connection(self.room_name, self.user)
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        if message_type == 'chat_message':
            message = text_data_json['message']
            username = text_data_json['username']
            time = text_data_json['time']
            message_id = str(uuid.uuid4())

            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'time': time,
                    'message_id' : message_id
                }
            )
        elif message_type == 'typing':
            username = text_data_json['username']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'typing',
                    'username': username
                }
            )
        elif message_type == 'stop_typing':
            username = text_data_json['username']
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'stop_typing',
                    'username': username
                }
            )

        elif message_type == 'file_message':
            file_name = text_data_json['file_name']
            file_url = text_data_json['file_url']
            username = text_data_json['username']
            message_id = str(uuid.uuid4())
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'file_message',
                    'file_name': file_name,
                    'file_url': file_url,
                    'username': username,
                    'message_id' : message_id
                }
            )

        elif message_type == 'reaction':
            reaction = text_data_json['reaction']
            message_id = text_data_json['message_id']
            username = text_data_json['username']
            
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'reaction',
                    'reaction': reaction,
                    'message_id': message_id,
                    'username': username
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        time = event['time']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'time': time,
            'message_id': message_id
        }))

    async def typing(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': username
        }))

    async def stop_typing(self, event):
        username = event['username']

        await self.send(text_data=json.dumps({
            'type': 'stop_typing',
            'username': username
        }))

    async def file_message(self, event):
        file_name = event['file_name']
        file_url = event['file_url']
        username = event['username']
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'type': 'file_message',
            'file_name': file_name,
            'file_url': file_url,
            'username': username,
            'message_id' : message_id
        }))

    async def reaction(self, event):
        reaction = event['reaction']
        message_id = event['message_id']
        username = event['username']
        
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'reaction': reaction,
            'message_id': message_id,
            'username': username
        }))
        


    async def send_message(self, event):
        message = event["message"]
        username = event["username"]
        time = event["time"]
        await self.send(text_data=json.dumps({"message": message, "username": username, "time": time}))

    @database_sync_to_async
    def find_or_create_room(self, user):
        
        available_room = PrivateChatRoom.objects.annotate(num_connections=Count('privateroomconnection')).filter(num_connections=1).first()
        if available_room:
            return available_room.name
        else:
            
            room_name = f"private_chat_{user.id}_{User.objects.order_by('?').first().id}"
            room, created = PrivateChatRoom.objects.get_or_create(name=room_name)
            return room.name

    @database_sync_to_async
    def add_connection(self, room, user):
        if PrivateRoomConnection.objects.filter(room=room).count() < 2:
            PrivateRoomConnection.objects.create(room=room, user=user)

    @database_sync_to_async
    def remove_connection(self, room_name, user):
        room = PrivateChatRoom.objects.get(name=room_name)
        PrivateRoomConnection.objects.filter(room=room, user=user).delete()



