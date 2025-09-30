"""
URL configuration for resume_optimizer project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('resume/', include('resume_analysis.urls')),
    path('tailor/', include('resume_tailoring.urls')),
    path('cover-letter/', include('cover_letter.urls')),
    path('interview/', include('interview_prep.urls')),
    path('stylist/', include('clothing_advisor.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

