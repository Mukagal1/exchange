from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ExchangeRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    from_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="offered_requests")
    to_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(
        max_length=10,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} предлагает {self.to_user} обмен {self.from_item} на {self.to_item}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    from_item = models.CharField(max_length=255)  # Название предмета отправителя
    to_item = models.CharField(max_length=255)    # Название предмета получателя
    is_read = models.BooleanField(default=False)  # Прочитано ли уведомление
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} хочет обменять '{self.from_item}' на '{self.to_item}'"

class GroupChat(models.Model):
    name = models.CharField(max_length=255)  # Название чата
    description = models.TextField(blank=True)  # Описание чата
    members = models.ManyToManyField(User, related_name="group_chats")  # Участники чата
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания

    def __str__(self):
        return self.name
    
class Chat(models.Model):
    name = models.CharField(max_length=255)  # Название чата
    description = models.TextField(blank=True)  # Описание чата
    members = models.ManyToManyField(User, related_name="chats")  # Участники чата
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания

    def __str__(self):
        return self.name

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")  # Связь с чатом
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")  # Отправитель
    content = models.TextField()  # Текст сообщения
    created_at = models.DateTimeField(auto_now_add=True)  # Дата отправки

    def __str__(self):
        return f"Сообщение от {self.sender.username} в чате '{self.chat.name}'"

class GroupMessage(models.Model):
    chat = models.ForeignKey(GroupChat, on_delete=models.CASCADE, related_name="messages")  # Связь с чатом
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages")  # Отправитель
    content = models.TextField()  # Текст сообщения
    created_at = models.DateTimeField(auto_now_add=True)  # Дата отправки

    def __str__(self):
        return f"Сообщение от {self.sender.username} в чате '{self.chat.name}'"