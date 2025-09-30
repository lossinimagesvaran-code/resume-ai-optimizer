from django import forms
from .models import ResumeUpload

class ResumeUploadForm(forms.ModelForm):
    """Form for uploading resume files"""
    class Meta:
        model = ResumeUpload
        fields = ['resume_file']
        widgets = {
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
                'id': 'resume-upload'
            })
        }

class JobDescriptionForm(forms.Form):
    """Form for job description input"""
    job_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 8,
            'placeholder': 'Paste the job description here...',
            'id': 'job-description'
        }),
        label='Job Description',
        required=True
    )
    
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name (optional)'
        }),
        required=False
    )
    
    job_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job Title (optional)'
        }),
        required=False
    )

