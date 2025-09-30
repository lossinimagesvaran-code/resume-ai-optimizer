from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ResumeAnalysis(models.Model):
    """Model to store resume analysis results"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_text = models.TextField()
    job_description = models.TextField()
    analysis_result = models.TextField()
    match_score = models.IntegerField(default=0)
    keywords_found = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Resume Analyses'
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Analysis for {username} - {self.created_at.strftime('%Y-%m-%d')}"

class ResumeUpload(models.Model):
    """Model to store uploaded resume files"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.original_filename} - {username}"

