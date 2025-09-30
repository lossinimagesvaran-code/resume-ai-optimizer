from django.urls import path
from . import views

app_name = 'resume_analysis'

urlpatterns = [
    path('', views.resume_analysis_home, name='home'),
    path('results/<int:analysis_id>/', views.analysis_results, name='results'),
    path('history/', views.analysis_history, name='history'),
    path('api/analyze/', views.api_analyze_resume, name='api_analyze'),
]


