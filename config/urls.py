from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Bizning API manzillarimiz
    path('', include('chatbot.urls')),
    
    # Autentifikatsiya (Login/Logout/Register) uchun DRF tayyor manzillari
    path('api-auth/', include('rest_framework.urls')),
]


# Media fayllar (profil rasmlari) uchun
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)