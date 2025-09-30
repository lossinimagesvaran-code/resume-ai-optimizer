from django.urls import path
from . import views

app_name = 'interview_prep'

urlpatterns = [
    path('', views.interview_home, name='home'),
    path('generate-tips/', views.generate_tips, name='generate_tips'),
    path('unlock-level/', views.unlock_level, name='unlock_level'),
    path('chat/', views.interview_coach_chat, name='chat'),
    path('tip/<int:tip_id>/complete/', views.mark_tip_completed, name='mark_tip_completed'),
    path('unlock-next-level/', views.unlock_next_level, name='unlock_next_level'),
    path('download-tips/', views.download_all_tips, name='download_tips'),
    path('clear-chat/', views.clear_chat_history, name='clear_chat'),
    path('api/generate-tips/', views.api_generate_tips, name='api_generate_tips'),
    path('api/chat-answer/', views.api_chat_answer, name='api_chat_answer'),
]

