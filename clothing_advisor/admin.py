from django.contrib import admin
from .models import SkinToneAnalysis, UserPreference, ChatSession

@admin.register(SkinToneAnalysis)
class SkinToneAnalysisAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'skin_tone', 'undertone', 'season', 'created_at']
    list_filter = ['skin_tone', 'undertone', 'season', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'product_id', 'liked', 'color', 'category', 'brand', 'created_at']
    list_filter = ['liked', 'color', 'category', 'brand', 'created_at']
    search_fields = ['session_id', 'product_id']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'gender', 'created_at', 'updated_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at', 'updated_at']
