from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, index

# Router yaratamiz va ViewSet-ni ro'yxatdan o'tkazamiz
router = DefaultRouter()
router.register(r'sessions', ChatViewSet, basename='chat')

urlpatterns = [
    # 1. Bosh sahifa (index.html) - BU DOIMO BIRINCHI TURISHI KERAK
    path('', index, name='index'),

    # 2. API manzillari - Routerni 'api/' prefiksi bilan ulaymiz
    # Shunda ular sessions/ emas, api/sessions/ bo'lib ishlaydi
    path('api/', include(router.urls)),
]