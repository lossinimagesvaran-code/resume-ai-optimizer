from django import forms
from .models import CoverLetter

class CoverLetterForm(forms.Form):
    """Form for cover letter generation"""
    # Personal Information
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Full Name'
        }),
        required=True
    )
    
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Your Address'
        }),
        required=True
    )
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Phone Number'
        }),
        required=False
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email Address'
        }),
        required=True
    )
    
    # Company Information
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name'
        }),
        required=True
    )
    
    company_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Company Address'
        }),
        required=False
    )
    
    job_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job Title/Position'
        }),
        required=True
    )
    
    # Cover Letter Options
    writing_style = forms.ChoiceField(
        choices=[
            ('professional', 'Professional & Formal'),
            ('enthusiastic', 'Enthusiastic & Energetic'),
            ('confident', 'Confident & Assertive'),
            ('friendly', 'Friendly & Approachable'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Writing Style',
        required=True,
        initial='professional'
    )
    
    focus_areas = forms.MultipleChoiceField(
        choices=[
            ('experience', 'Highlight Relevant Experience'),
            ('skills', 'Emphasize Key Skills'),
            ('achievements', 'Showcase Achievements'),
            ('education', 'Feature Educational Background'),
            ('passion', 'Express Passion for the Role'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'focus-checkboxes'
        }),
        label='Focus Areas',
        required=False
    )
    
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional information you want to include...'
        }),
        label='Additional Notes',
        required=False
    )

class CoverLetterCustomizationForm(forms.Form):
    """Form for customizing generated cover letter"""
    custom_content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Edit your cover letter content here...'
        }),
        label='Cover Letter Content',
        required=True
    )
    
    font_size = forms.ChoiceField(
        choices=[
            ('small', 'Small (10pt)'),
            ('medium', 'Medium (12pt)'),
            ('large', 'Large (14pt)'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Font Size',
        required=True,
        initial='medium'
    )
    
    line_spacing = forms.ChoiceField(
        choices=[
            ('single', 'Single Spacing'),
            ('1.5', '1.5 Line Spacing'),
            ('double', 'Double Spacing'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Line Spacing',
        required=True,
        initial='1.5'
    )

