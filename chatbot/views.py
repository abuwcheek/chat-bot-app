import os
from django.http import JsonResponse
from dotenv import load_dotenv
from groq import Groq

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer
from .forms import UserRegistrationForm


# .env yuklash
load_dotenv()


# Groq klientini bir marta global e'lon qilamiz
client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def index(request, chat_id=None):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'index.html')



def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('index')
        else:
            messages.error(request, "Formada xatolik bor.")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Tizimga kirdingiz!")
            return redirect('index')
        else:
            messages.error(request, "Email yoki parol noto'g'ri!")
    return render(request, 'login.html')



def logout_view(request):
    auth_logout(request)
    return redirect('login')



class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_bot_response(self, user_text):
        """ 
        AI bilan muloqot qiluvchi funksiya.
        Sizning 20 ta qoidangiz O'ZGARISHSIZ saqlangan.
        """
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": """
                        Sen faqat savol-javob qiladigan aqlli yordamchisan. 
                        Quyidagi qat'iy qoidalarga amal qil:
                        1. FAQAT O'ZBEK TILIDA GAPIR.
                        2. Javoblar 1-2 gapdan oshmasin (lo'nda bo'lsin).
                        3. Odobsiz so'zlarni aslo ishlatma.
                        4. Agar senga 'qalay', 'qalaysan' kabi salomlashishsa, FAQAT 'Yaxshi, rahmat' deb javob ber.
                        5. O'zing haqingda (AI ekanliging haqida) gapirib vaqtni olma.
                        6. Agar savol tushunarsiz yoki bema'ni bo'lsa, 'Iltimos, aniqroq so'rang' deb javob ber.
                        7. Hech qachon foydalanuvchidan shaxsiy ma'lumotlarni so'rama yoki ularni javoblaringga qo'shma.
                        8. Agar foydalanuvchi shaxsiy ma'lumotlarni bersa, ularni javoblaringda ishlatma va 'Shaxsiy ma'lumotlaringizni saqlang, ular haqida gapirmaymiz' deb javob ber.
                        9. Javoblaringni doimo hurmatli va samimiy tut.
                        10. Agar foydalanuvchi noto'g'ri yoki zararli so'rov yuborsa, 'Uzr, bu so'rovga javob bera olmayman' deb javob ber.
                        11. Hech qachon foydalanuvchini noto'g'ri yolga solma yoki zararli maslahatlar berma.
                        12. Agar foydalanuvchi juda ko'p savollar bersa, 'Siz juda ko'p savollar berdingiz, iltimos, biroz kuting' deb javob ber.
                        13. Agar foydalanuvchi kod tahlil yoki texnik savollar bersa, 'Uzr, hozircha bu so'rovga javob bera olmayman' deb javob ber.
                        14. Agar foydalanuvchi yordam so'rovi bersa, 'Uzr, hozircha bu so'rovga javob bera olmayman' deb javob ber.
                        15. Agar nima qila olasan deb so'rasa 'Men savol-javob qilaman, lekin kod tahlil yoki texnik yordam bera olmayman' deb javob ber.
                        16. Agar foydalanuvchi juda ko'p shaxsiy ma'lumotlarni bersa, 'Siz juda ko'p shaxsiy ma'lumotlar berdingiz, iltimos, ehtiyot bo'ling' deb javob ber.
                        17. Kun davomida boladigan gaplardan va ijtimoiy savollar bersa qisqa lo'nda javob berishing kerak, masalan 'Bugun ob-havo qanday?' deb so'rasa 'Bugun ob-havo yaxshi' deb javob ber.
                        18. Ichtimoiy tarmoqlar, yangiliklar, siyosat, sport va boshqa mavzularda savollar bersa 'Men hozircha bunday savollarga javob bera olmayman' deb javob ber.
                        19. Kimnidir tanqid qilish yoki salbiy gaplar bo'lsa, 'Uzr, bu mavzu haqida gapira olmayman' deb javob ber.
                        20. Biror kishini hayoti va ijodi kitoblari sherlari asaralari haqida savollar bersa 'Uzr, bu mavzu haqida gapira olmayman' deb javob ber.
                        """
                    },
                    {"role": "user", "content": user_text},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,  # 0.4 dan 0.7 ga o'zgartirdik
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "Xatolik: AI bilan aloqa uzildi."



    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        session = self.get_object()
        user_text = request.data.get('text')

        if not user_text:
            return Response({"error": "Matn bo'sh"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. User xabarini saqlash
        user_msg = Message.objects.create(session=session, sender_type='user', text=user_text)

        # 2. Sarlavhani yangilash
        if session.messages.count() <= 2:
            session.title = user_text[:30] + "..." if len(user_text) > 30 else user_text
            session.save()

        # 3. AI dan javob olish
        bot_response_text = self.get_bot_response(user_text)

        # 4. Bot xabarini saqlash
        bot_msg = Message.objects.create(session=session, sender_type='bot', text=bot_response_text)

        return Response({
            "session_title": session.title,
            "user_message": MessageSerializer(user_msg).data,
            "bot_message": MessageSerializer(bot_msg).data
        }, status=status.HTTP_201_CREATED)
    
