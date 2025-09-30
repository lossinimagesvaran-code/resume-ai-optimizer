from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TailoredResume(models.Model):
    """Model to store tailored resume versions"""
    TEMPLATE_CHOICES = [
        ('traditional', 'Traditional'),
        ('modern', 'Modern'),
        ('hybrid', 'Hybrid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    original_resume = models.TextField()
    job_description = models.TextField()
    tailored_content = models.TextField()
    template_used = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, null=False, blank=False)
    match_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.get_template_used_display()} Resume - {username}"

class ResumeTemplate(models.Model):
    """Model to store resume template configurations"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    template_config = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


