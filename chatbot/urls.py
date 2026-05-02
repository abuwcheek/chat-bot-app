from dj_rest_auth import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, index, register, login_view, logout_view # Yangi funksiyalarni qo'shdik

# Router yaratamiz va ViewSet-ni ro'yxatdan o'tkazamiz
router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')



urlpatterns = [
    # 1. Bosh sahifa (index.html)
    path('', index, name='index'),

    # 2. Avtorizatsiya manzillari (Auth)
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('chat/<uuid:chat_id>/', index, name='chat_detail'),

    # 3. API manzillari - Routerni 'api/' prefiksi bilan ulaymiz
    path('api/', include(router.urls)),
]