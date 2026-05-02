from django.contrib import admin
from .models import Profile, ChatSession, Message



# 1. Xabarlarni ChatSession ichida "Inline" (ichma-ich) ko'rsatish
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0 
    # UUID ishlatganimiz uchun bu yerda muammo bo'lmasligi kerak
    readonly_fields = ('sender_type', 'text', 'created_at') 
    can_delete = True



# 2. Chat sessiyalarini boshqarish
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    # 'id' (UUID) ni ro'yxatda ko'rsatish qidiruv va tekshiruv uchun foydali
    list_display = ('title', 'user', 'id', 'updated_at') 
    list_filter = ('user', 'created_at', 'updated_at')
    search_fields = ('title', 'id', 'user__username')
    inlines = [MessageInline]
    
    # Kecha kelishganimizdek, eng oxirgi yozishilgan chat tepada tursin
    ordering = ('-updated_at',)



# 3. Xabarlarni alohida ko'rish (monitoring uchun)
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender_type', 'text_preview', 'created_at')
    list_filter = ('sender_type', 'created_at')
    search_fields = ('text', 'session__title')

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Xabar matni"



# 4. Foydalanuvchi profillarini boshqarish
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_status', 'created_at')
    
    def avatar_status(self, obj):
        if obj.avatar:
            return "✅ Rasm yuklangan"
        return "❌ Rasm yo'q"
    avatar_status.short_description = "Avatar holati"