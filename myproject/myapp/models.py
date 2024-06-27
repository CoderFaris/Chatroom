from django.db import models
from django.contrib.auth.models import User

class PrivateChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)

class PrivateRoomConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    connected_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'room')


class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.content}'

    @staticmethod
    def last_10_messages():
        return Message.objects.order_by('-timestamp').all()[:10]
    
class PrivateMessage(models.Model):
    room = models.ForeignKey(PrivateChatRoom, related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='private_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.content}'
    
    @staticmethod
    def last_10_messages(room):
        return PrivateMessage.objects.filter(room=room).order_by('-timestamp').all()[:10]


    

