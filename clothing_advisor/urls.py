from django.urls import path
from . import views

app_name = 'clothing_advisor'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/analyze-skin-tone/', views.analyze_skin_tone, name='analyze_skin_tone'),
    path('api/get-recommendations/', views.get_recommendations, name='get_recommendations'),
    path('api/submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/get-chat-history/', views.get_chat_history, name='get_chat_history'),
    path('api/end-session/', views.end_session, name='end_session'),
]
