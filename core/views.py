from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resume_analysis.models import ResumeAnalysis

def home(request):
    """Home page view"""
    recent_analysis = ResumeAnalysis.objects.first()
    context = {
        'recent_analysis': recent_analysis,
    }
    return render(request, 'core/home.html', context)

def dashboard(request):
    """Dashboard view"""
    recent_analysis = ResumeAnalysis.objects.first()
    context = {
        'recent_analysis': recent_analysis,
    }
    return render(request, 'core/dashboard.html', context)

def about(request):
    """About page view"""
    recent_analysis = ResumeAnalysis.objects.first()
    context = {
        'recent_analysis': recent_analysis,
    }
    return render(request, 'core/about.html', context)


