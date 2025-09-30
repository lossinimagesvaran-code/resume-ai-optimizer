from django import forms
from .models import TailoredResume

# Define template choices at module level to ensure consistency
TEMPLATE_CHOICES = [
    ('traditional', 'Traditional - Linear layout with clear section separators'),
    ('modern', 'Modern - Spaced-out layout with creative skill grouping'),
    ('hybrid', 'Hybrid - Skill-focused layout with flexible structure'),
]

class ResumeTailoringForm(forms.Form):
    """Form for resume tailoring options"""
    
    template_choice = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'template-radio'
        }),
        label='Choose Resume Template',
        required=True,
        initial=None
    )
    
    def clean_template_choice(self):
        template_choice = self.cleaned_data.get('template_choice')
        valid_choices = ['traditional', 'modern', 'hybrid']
        if template_choice not in valid_choices:
            raise forms.ValidationError(f'Invalid template choice. Must be one of: {", ".join(valid_choices)}')
        return template_choice
    

class ResumeCustomizationForm(forms.Form):
    """Form for customizing tailored resume"""
    custom_skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any specific skills you want to highlight...'
        }),
        label='Custom Skills to Add',
        required=False
    )
    
    remove_sections = forms.MultipleChoiceField(
        choices=[
            ('summary', 'Professional Summary'),
            ('skills', 'Skills Section'),
            ('experience', 'Work Experience'),
            ('education', 'Education'),
            ('certifications', 'Certifications'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'remove-checkboxes'
        }),
        label='Sections to Remove',
        required=False
    )
    
    additional_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any additional notes for customization...'
        }),
        label='Additional Notes',
        required=False
    )


