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
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.author.message
    
    def last_10_messages(self):
        return Message.objects.order_by('-timestamp').all()[:10]


    

