from rest_framework import serializers
from .models import Profile, ChatSession, Message
from django.contrib.auth.models import User



# Foydalanuvchi ma'lumotlari uchun
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']



# Har bir xabar uchun
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_type', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']



# Chat tarixi (sessiyalar) uchun
class ChatSessionSerializer(serializers.ModelSerializer):
    # Sessiya ichidagi barcha xabarlarni chiqarish uchun (optional)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']



# Profil ma'lumotlari uchun
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'avatar', 'created_at']