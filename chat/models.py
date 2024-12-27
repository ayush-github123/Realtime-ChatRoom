from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Message(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}..."  # Short preview of the message
    