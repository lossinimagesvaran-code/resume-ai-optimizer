import os
from typing import List, Dict, Any
import google.generativeai as genai
from django.conf import settings
import random
import json

class StyleAdvisorAgent:
    """
    Main AI agent that acts as a virtual stylist using Google Gemini
    Provides conversational recommendations with explanations and compliments
    """
    
    def __init__(self):
        try:
            self.api_key = settings.GOOGLE_API_KEY
            if not self.api_key or self.api_key == 'your-google-gemini-api-key-here':
                print("Warning: Google API key not configured properly")
                self.model = None
            else:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Error initializing AI agent: {e}")
            self.model = None
        
        # Personality and style guidelines
        self.personality_prompt = """
        You are Style Advisor, a friendly and knowledgeable AI fashion stylist specializing in professional interview attire. 
        You have expertise in color theory, skin tone analysis, and professional dress codes.
        
        Your personality:
        - Warm, encouraging, and confidence-boosting
        - Professional but approachable
        - Knowledgeable about fashion and color theory
        - Supportive and motivational
        - Uses fashion terminology appropriately but keeps explanations accessible
        
        Your expertise includes:
        - Seasonal color analysis
        - Interview-appropriate clothing
        - Color theory and skin tone matching
        - Professional styling tips
        - Confidence-building through fashion
        """
    
    def generate_greeting(self, gender: str, skin_tone: str, season: str) -> str:
        """Generate a personalized greeting message"""
        prompt = f"""
        {self.personality_prompt}
        
        Generate a warm, welcoming greeting for a {gender.lower()} user who has just uploaded their photo for skin tone analysis.
        
        Their analysis results:
        - Skin tone: {skin_tone}
        - Season: {season}
        
        The greeting should:
        1. Welcome them warmly
        2. Briefly mention their skin tone results
        3. Express excitement about helping them find interview outfits
        4. Set expectations for the recommendation process
        5. Be encouraging and confidence-building
        
        Keep it conversational and under 100 words.
        """
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            else:
                raise Exception("AI model not initialized")
        except Exception as e:
            print(f"AI generation error: {e}")
            return f"Hello! I'm your AI Style Advisor. I've analyzed your skin tone and found that you have beautiful {skin_tone.replace('_', ' ')} undertones, perfect for {season} colors! I'm excited to help you find the perfect interview outfits that will make you look confident and professional. Let me show you some amazing options!"
    
    def generate_outfit_explanation(self, outfit: Dict, skin_tone: str, 
                                  season: str, gender: str) -> str:
        """Generate explanation for why an outfit works for the user"""
        items_description = []
        for item in outfit['items']:
            items_description.append(f"{item['color']} {item['category'].lower()} from {item['brand']}")
        
        outfit_description = ", ".join(items_description)
        
        prompt = f"""
        {self.personality_prompt}
        
        Explain why this outfit works perfectly for a {gender.lower()} with {skin_tone.replace('_', ' ')} skin tone ({season} season):
        
        Outfit: {outfit_description}
        Total Price: ${outfit['total_price']}
        
        Your explanation should:
        1. Reference color theory and how the colors complement their skin tone
        2. Mention why it's appropriate for interviews
        3. Highlight the professional impact
        4. Be encouraging and confidence-building
        5. Keep it concise (2-3 sentences max)
        
        Focus on the color harmony and professional appearance.
        """
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            else:
                raise Exception("AI model not initialized")
        except Exception as e:
            print(f"AI outfit explanation error: {e}")
            primary_color = outfit.get('primary_colors', ['neutral'])[0] if outfit.get('primary_colors') else 'neutral'
            return f"This {primary_color} combination beautifully complements your {season} coloring and creates a polished, professional look that's perfect for interviews. The color harmony will enhance your natural features and project confidence."
    
    def generate_compliment(self, outfit: Dict, gender: str) -> str:
        """Generate a personalized compliment for the outfit"""
        compliments = [
            "You'll look absolutely stunning and confident in this outfit!",
            "This combination will make you shine with professional elegance!",
            "You're going to impress everyone with this polished, sophisticated look!",
            "This outfit perfectly balances professionalism with your personal style!",
            "You'll feel empowered and ready to conquer that interview!",
            "This look will highlight your best features and boost your confidence!",
            "You're going to look like the accomplished professional you are!",
            "This ensemble will make you feel unstoppable and interview-ready!"
        ]
        
        return random.choice(compliments)
    
    def generate_feedback_response(self, feedback: str, user_preferences: Dict,
                                 skin_tone: str, season: str, gender: str) -> str:
        """Generate response to user feedback (like/dislike)"""
        if feedback == 'like':
            responses = [
                "Wonderful choice! I can see you have great taste. Let me find more options in similar styles and colors.",
                "Perfect! I love that you're drawn to these colors - they really suit you beautifully.",
                "Excellent! I'll remember your preference for these types of pieces and colors.",
                "Great selection! Your instincts are spot-on for what works with your coloring."
            ]
        else:  # dislike
            responses = [
                "No worries at all! Everyone has different style preferences. Let me show you some alternatives.",
                "That's perfectly fine! Let me find some different options that might be more your style.",
                "I understand - personal style is so important! Let me try a different approach.",
                "Thanks for the feedback! Let me explore some other color combinations for you."
            ]
        
        return random.choice(responses)
    
    def generate_alternative_suggestion(self, avoided_items: List[str], 
                                      skin_tone: str, season: str) -> str:
        """Generate suggestion for alternative options"""
        prompt = f"""
        {self.personality_prompt}
        
        The user didn't like these items: {', '.join(avoided_items)}
        Their skin tone: {skin_tone.replace('_', ' ')} ({season} season)
        
        Generate a brief, encouraging message suggesting we'll find alternatives that better match their style.
        Mention exploring different colors or styles within their seasonal palette.
        Keep it positive and solution-focused (1-2 sentences).
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Let me find some different options that better match your personal style while still working beautifully with your {season} coloring!"
    
    def generate_final_motivation(self, gender: str, total_outfits_shown: int) -> str:
        """Generate final motivational message for the interview"""
        motivational_messages = [
            f"You've got this! With these {total_outfits_shown} amazing outfit options, you're fully prepared to make a fantastic first impression. Remember, confidence is your best accessory - wear it proudly!",
            f"I'm so excited for your interview! Any of these {total_outfits_shown} outfits will help you look polished and professional. Trust in your abilities and let your personality shine through!",
            f"You're going to do wonderfully! These outfit choices will help you feel confident and comfortable, which is exactly what you need to succeed. Best of luck with your interview!",
            f"Perfect! You now have {total_outfits_shown} interview-ready looks that complement your natural beauty. Remember, you've got the skills and the style - now go show them what you're made of!"
        ]
        
        return random.choice(motivational_messages)

class ColorTheoryAgent:
    """
    Specialized agent for color theory and skin tone matching
    """
    
    def __init__(self):
        self.color_theory_rules = {
            'spring': {
                'best_colors': ['coral', 'peach', 'warm yellow', 'golden brown', 'bright green', 'aqua', 'ivory'],
                'avoid_colors': ['black', 'pure white', 'cool blue', 'purple', 'grey'],
                'interview_safe': ['navy', 'cream', 'light blue', 'soft pink', 'warm grey']
            },
            'summer': {
                'best_colors': ['lavender', 'powder blue', 'soft pink', 'mauve', 'gray-blue', 'periwinkle'],
                'avoid_colors': ['orange', 'bright yellow', 'warm brown', 'gold', 'black'],
                'interview_safe': ['navy', 'light grey', 'powder blue', 'soft pink', 'periwinkle']
            },
            'autumn': {
                'best_colors': ['olive green', 'rust', 'terracotta', 'mustard yellow', 'warm brown', 'teal'],
                'avoid_colors': ['pink', 'cool blue', 'purple', 'pure white', 'black'],
                'interview_safe': ['navy', 'warm brown', 'olive green', 'cream', 'deep teal']
            },
            'winter': {
                'best_colors': ['pure white', 'black', 'navy blue', 'royal purple', 'emerald green', 'bright pink'],
                'avoid_colors': ['beige', 'orange', 'yellow', 'brown', 'peach'],
                'interview_safe': ['navy', 'black', 'pure white', 'grey', 'deep purple']
            }
        }
    
    def get_color_recommendations(self, season: str, context: str = 'interview') -> Dict:
        """Get color recommendations based on season and context"""
        season_data = self.color_theory_rules.get(season, self.color_theory_rules['winter'])
        
        if context == 'interview':
            return {
                'recommended': season_data['interview_safe'],
                'explanation': f"These colors work beautifully with {season} coloring and are perfect for professional interviews."
            }
        else:
            return {
                'recommended': season_data['best_colors'],
                'avoid': season_data['avoid_colors'],
                'explanation': f"These colors enhance {season} skin tones naturally."
            }
    
    def explain_color_choice(self, color: str, season: str, skin_tone: str) -> str:
        """Explain why a specific color works for the user"""
        explanations = {
            'navy': f"Navy is universally flattering and creates a sophisticated, trustworthy impression perfect for {season} coloring.",
            'black': f"Black provides strong contrast that enhances {season} features and projects authority and professionalism.",
            'white': f"Crisp white brightens {season} complexions and creates a clean, polished professional appearance.",
            'grey': f"Grey is a versatile neutral that complements {season} undertones while maintaining professional elegance.",
            'blue': f"Blue tones harmonize beautifully with {season} coloring and convey reliability and competence.",
            'brown': f"Warm brown shades enhance {season} natural warmth and create an approachable yet professional look.",
            'green': f"Green tones work wonderfully with {season} coloring and suggest growth, harmony, and reliability."
        }
        
        return explanations.get(color.lower(), f"This {color} shade complements your {season} coloring beautifully.")

class PreferenceAgent:
    """
    Agent for learning and applying user preferences
    """
    
    def __init__(self):
        self.preference_weights = {
            'color': 3,
            'brand': 2,
            'category': 2,
            'price_range': 1
        }
    
    def analyze_preferences(self, user_feedback: List[Dict]) -> Dict:
        """Analyze user feedback to extract preferences"""
        liked_colors = []
        disliked_colors = []
        liked_brands = []
        disliked_brands = []
        liked_categories = []
        disliked_categories = []
        
        for feedback in user_feedback:
            if feedback['liked']:
                liked_colors.append(feedback['color'].lower())
                liked_brands.append(feedback['brand'].lower())
                liked_categories.append(feedback['category'].lower())
            else:
                disliked_colors.append(feedback['color'].lower())
                disliked_brands.append(feedback['brand'].lower())
                disliked_categories.append(feedback['category'].lower())
        
        return {
            'liked_colors': list(set(liked_colors)),
            'disliked_colors': list(set(disliked_colors)),
            'liked_brands': list(set(liked_brands)),
            'disliked_brands': list(set(disliked_brands)),
            'liked_categories': list(set(liked_categories)),
            'disliked_categories': list(set(disliked_categories))
        }
    
    def generate_personalized_message(self, preferences: Dict) -> str:
        """Generate a message acknowledging user preferences"""
        messages = []
        
        if preferences['liked_colors']:
            colors = ', '.join(preferences['liked_colors'][:3])
            messages.append(f"I can see you love {colors} - great choice!")
        
        if preferences['liked_brands']:
            brands = ', '.join(preferences['liked_brands'][:2])
            messages.append(f"I've noted your preference for {brands}.")
        
        if preferences['disliked_colors']:
            colors = ', '.join(preferences['disliked_colors'][:2])
            messages.append(f"I'll avoid {colors} in future recommendations.")
        
        if not messages:
            return "I'm learning your style preferences to give you better recommendations!"
        
        return " ".join(messages)
