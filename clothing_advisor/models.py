from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class SkinToneAnalysis(models.Model):
    """Model to store skin tone analysis results"""
    SKIN_TONE_CHOICES = [
        ('deep_warm', 'Deep Warm'),
        ('deep_cool', 'Deep Cool'),
        ('tan_warm', 'Tan Warm'),
        ('medium_warm', 'Medium Warm'),
        ('medium_cool', 'Medium Cool'),
        ('olive_cool', 'Olive Cool'),
        ('fair_warm', 'Fair Warm'),
        ('light_cool', 'Light Cool'),
    ]
    
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    uploaded_image = models.ImageField(upload_to='skin_analysis/')
    skin_tone = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES)
    undertone = models.CharField(max_length=10, choices=[('warm', 'Warm'), ('cool', 'Cool')])
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    rgb_values = models.JSONField()  # Store average RGB values
    hsv_values = models.JSONField()  # Store average HSV values
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.skin_tone} ({self.season})"

class UserPreference(models.Model):
    """Model to store user preferences and feedback"""
    session_id = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)  # From CSV dataset
    liked = models.BooleanField()  # True for like, False for dislike
    color = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['session_id', 'product_id']
    
    def __str__(self):
        return f"Session {self.session_id} - {'Liked' if self.liked else 'Disliked'} {self.product_id}"

class ChatSession(models.Model):
    """Model to store chat conversation history"""
    session_id = models.CharField(max_length=100, unique=True)
    gender = models.CharField(max_length=10, choices=[('Men', 'Men'), ('Women', 'Women')])
    conversation_history = models.JSONField(default=list)
    current_recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_message(self, role, content, recommendations=None):
        """Add a message to the conversation history"""
        import json
        from datetime import datetime
        
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': str(content),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Ensure conversation_history is a list
        if not isinstance(self.conversation_history, list):
            self.conversation_history = []
        
        # Add message to history
        self.conversation_history.append(message)
        
        # Handle recommendations separately to avoid JSON issues
        if recommendations:
            try:
                # Serialize recommendations to ensure JSON compatibility
                serializable_recommendations = []
                for rec in recommendations:
                    if isinstance(rec, dict):
                        # Clean the recommendation to ensure JSON serialization
                        clean_rec = {
                            'outfit_id': str(rec.get('outfit_id', '')),
                            'total_price': float(rec.get('total_price', 0)),
                            'explanation': str(rec.get('explanation', '')),
                            'compliment': str(rec.get('compliment', '')),
                            'items': []
                        }
                        
                        # Clean items
                        for item in rec.get('items', []):
                            if isinstance(item, dict):
                                # Handle NaN and None values properly
                                def clean_value(val):
                                    if val is None or str(val).lower() == 'nan':
                                        return ''
                                    return str(val)
                                
                                clean_item = {
                                    'category': clean_value(item.get('category', '')),
                                    'name': clean_value(item.get('name', '')),
                                    'color': clean_value(item.get('color', '')),
                                    'brand': clean_value(item.get('brand', '')),
                                    'price': clean_value(item.get('price', '')),
                                    'image_url': clean_value(item.get('image_url', '')),
                                    'product_url': clean_value(item.get('product_url', ''))
                                }
                                clean_rec['items'].append(clean_item)
                        
                        serializable_recommendations.append(clean_rec)
                
                self.current_recommendations = serializable_recommendations
            except Exception as e:
                print(f"Error serializing recommendations: {e}")
                self.current_recommendations = []
        
        self.save()
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.gender}"