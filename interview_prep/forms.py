from django import forms
from .models import InterviewTip

class InterviewQuestionForm(forms.Form):
    """Form for asking interview questions"""
    question = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ask your interview coach anything...',
            'id': 'interview-question'
        }),
        label='Your Question',
        required=True
    )

class TipCompletionForm(forms.Form):
    """Form for marking tips as completed"""
    tip_id = forms.IntegerField(widget=forms.HiddenInput())
    is_completed = forms.BooleanField(required=False)

class InterviewPrepForm(forms.Form):
    """Form for interview preparation preferences"""
    job_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Software Engineer'
        }),
        label='Job Title',
        required=False
    )
    
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Google'
        }),
        label='Company Name',
        required=False
    )
    
    experience_level = forms.ChoiceField(
        choices=[
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level'),
            ('executive', 'Executive Level'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Experience Level',
        required=True,
        initial='mid'
    )
    
    interview_type = forms.ChoiceField(
        choices=[
            ('behavioral', 'Behavioral'),
            ('technical', 'Technical'),
            ('case_study', 'Case Study'),
            ('panel', 'Panel Interview'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Interview Type',
        required=True,
        initial='behavioral'
    )

