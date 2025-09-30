from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InterviewTip(models.Model):
    """Model to store interview preparation tips"""
    LEVEL_CHOICES = [
        (1, 'Level 1 - Essential'),
        (2, 'Level 2 - Advanced'),
        (3, 'Level 3 - Expert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    tip_content = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['level', 'created_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Level {self.level} Tip - {username}"

class InterviewChat(models.Model):
    """Model to store interview coach chat history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Chat - {username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class InterviewSession(models.Model):
    """Model to store interview preparation session data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.CharField(max_length=200, default='Not specified')
    company_name = models.CharField(max_length=200, default='Not specified')
    interview_type = models.CharField(max_length=100, default='behavioral')
    experience_level = models.CharField(max_length=50, default='mid')
    tips_generated = models.TextField(blank=True, null=True)
    current_level = models.IntegerField(default=1)
    tips_completed = models.IntegerField(default=0)
    total_tips = models.IntegerField(default=0)
    session_started = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Session - {username} - Level {self.current_level}"
    
    def get_progress_percentage(self):
        """Calculate progress percentage for current level"""
        if self.total_tips == 0:
            return 0
        return (self.tips_completed / self.total_tips) * 100

