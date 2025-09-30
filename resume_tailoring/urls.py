from django.urls import path
from . import views

app_name = 'resume_tailoring'

urlpatterns = [
    path('', views.tailoring_home, name='home'),
    path('customize/', views.customize_resume, name='customize'),
    path('preview/<int:resume_id>/', views.preview_resume, name='preview'),
    path('download/<int:resume_id>/<str:format_type>/', views.download_resume, name='download'),
    path('download-edited/<int:resume_id>/', views.download_edited_resume, name='download_edited'),
    path('history/', views.resume_history, name='history'),
    path('reset-template/', views.reset_template, name='reset_template'),
    path('reset-session/', views.reset_session, name='reset_session'),
]

