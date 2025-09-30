from django.urls import path
from . import views

app_name = 'cover_letter'

urlpatterns = [
    path('', views.cover_letter_home, name='home'),
    path('generate/', views.generate_cover_letter, name='generate'),
    path('preview/<int:letter_id>/', views.preview_cover_letter, name='preview'),
    path('download/<int:letter_id>/<str:format_type>/', views.download_cover_letter, name='download'),
    path('history/', views.cover_letter_history, name='history'),
    path('edit/<int:letter_id>/', views.edit_cover_letter, name='edit'),
    path('clear-session/', views.clear_cover_letter_session, name='clear_session'),
]

