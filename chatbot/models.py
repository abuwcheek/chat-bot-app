from django.db import models
from django.contrib.auth.models import User
import uuid



# Barcha modellar uchun umumiy tayanch model
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



# Foydalanuvchi shaxsiy ma'lumotlari (Ism, Familiya, Rasm)
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, verbose_name="Ism")
    last_name = models.CharField(max_length=100, verbose_name="Familiya")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Profil rasmi")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon raqami")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.email})"



# Chat sessiyalari
class ChatSession(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, default="Yangi suhbat")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.id})"



# Xabarlar
class Message(BaseModel):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    text = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_type}: {self.text[:30]}"