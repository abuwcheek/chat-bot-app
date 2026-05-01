from rest_framework import viewsets, status
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message, Profile
from .serializers import ChatSessionSerializer, MessageSerializer



def index(request):
    return render(request, 'index.html')



class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Foydalanuvchi faqat o'ziga tegishli chatlarni ko'radi
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Yangi chat ochilganda uni joriy userga bog'laymiz
        serializer.save(user=self.request.user)



    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Xabar yuborish, chat nomini yangilash va bot javobini olish"""
        session = self.get_object()
        user_text = request.data.get('text')

        if not user_text:
            return Response({"error": "Xabar matni bo'sh bo'lishi mumkin emas"}, status=status.HTTP_400_BAD_REQUEST)

        # --- CHAT NOMINI YANGILASH MANTIQI (BIRINCHI XABAR UCHUN) ---
        # Agar sessiyada hali birorta xabar bo'lmasa, demak bu birinchi muloqot
        if not session.messages.exists():
            # Matnning birinchi 30 ta belgisini olamiz (nom sifatida)
            new_title = user_text[:30] + "..." if len(user_text) > 30 else user_text
            session.title = new_title
            session.save()
        # ----------------------------------------------------------

        # 1. Foydalanuvchi xabarini saqlash
        user_msg = Message.objects.create(
            session=session,
            sender_type='user',
            text=user_text
        )

        # 2. Bot mantiqi (Rule-based)
        bot_response_text = self.get_bot_response(user_text)

        # 3. Bot javobini saqlash
        bot_msg = Message.objects.create(
            session=session,
            sender_type='bot',
            text=bot_response_text
        )

        # Yangilangan xabarlarni va yangi title-ni qaytarish
        return Response({
            "session_id": session.id,
            "session_title": session.title, # Frontendda sidebar yangilanishi uchun muhim
            "user_message": MessageSerializer(user_msg).data,
            "bot_message": MessageSerializer(bot_msg).data
        }, status=status.HTTP_201_CREATED)



    def get_bot_response(self, text):
        """Oddiy mantiqiy qoidalar"""
        text = text.lower()
        if "salom" in text:
            return "Assalomu alaykum! Qanday yordam bera olaman?"
        elif "uzbekistan" in text or "o'zbekiston" in text:
            return "O'zbekiston - Markaziy Osiyodagi go'zal va mehmondo'st davlat!"
        elif "vaqt" in text:
            import datetime
            return f"Hozirgi vaqt: {datetime.datetime.now().strftime('%H:%M')}"
        else:
            return "Kechirasiz, men hali buni tushunmayman. Boshqa narsa so'rab ko'ring."