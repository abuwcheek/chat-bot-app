from django.contrib import admin
from .models import Profile, ChatSession, Message



# 1. Xabarlarni ChatSession ichida "Inline" (ichma-ich) ko'rsatish uchun
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0 # Bo'sh qatorlar chiqarmaslik uchun
    readonly_fields = ('sender_type', 'text', 'created_at') # Admin xabarlarni o'zgartira olmasligi uchun
    can_delete = True



# 2. Chat sessiyalarini boshqarish
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'id', 'created_at', 'updated_at') # Ro'yxatda ko'rinadigan ustunlar
    list_filter = ('user', 'created_at') # O'ng tomondagi filtrlar
    search_fields = ('title', 'id', 'user__username') # Qidiruv maydoni
    inlines = [MessageInline] # Sessiyaga kirganda uning ichidagi xabarlarni ham ko'rish
    ordering = ('-created_at',) # Eng yangi sessiyalar tepada tursin



# 3. Xabarlarni alohida ko'rish
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender_type', 'text_preview', 'created_at')
    list_filter = ('sender_type', 'created_at')
    search_fields = ('text', 'session__title')

    # Xabar matni uzun bo'lsa, qisqartirib ko'rsatish
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Xabar matni"



# 4. Foydalanuvchi profillarini boshqarish
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_preview', 'created_at')
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return "Rasm yuklangan"
        return "Rasm yo'q"
    avatar_preview.short_description = "Avatar holati"