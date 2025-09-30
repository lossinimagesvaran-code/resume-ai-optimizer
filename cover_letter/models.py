from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CoverLetter(models.Model):
    """Model to store generated cover letters"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    cover_letter_content = models.TextField()
    personal_info = models.JSONField()  # Store name, address, etc.
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Cover Letter for {self.job_title} at {self.company_name} - {username}"

class CoverLetterTemplate(models.Model):
    """Model to store cover letter templates"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    template_content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

