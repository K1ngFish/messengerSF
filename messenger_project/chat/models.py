from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat_group = models.ForeignKey('ChatGroup', related_name='messages', on_delete=models.CASCADE, null=True,
                                   blank=True)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, default=1)



    def __str__(self):
        return self.author.username

class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='chat_groups')
    creator = models.ForeignKey(User, related_name='created_chat_groups', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def add_member(self, user):
        self.members.add(user)

    def remove_member(self, user):
        self.members.remove(user)

    def change_name(self, new_name):
        self.name = new_name
        self.save()

