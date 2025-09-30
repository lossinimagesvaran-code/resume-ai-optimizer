from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
import json
import uuid
import base64
from PIL import Image
import io
import traceback

from .models import SkinToneAnalysis, UserPreference, ChatSession
from .skin_tone_detector import SkinToneDetector
from .fashion_dataset import FashionDatasetManager
from .ai_agents import StyleAdvisorAgent, ColorTheoryAgent, PreferenceAgent

def index(request):
    """Render the main chat interface"""
    return render(request, 'clothing_advisor/stylist.html')

@csrf_exempt
@require_http_methods(["POST"])
def analyze_skin_tone(request):
    """
    Analyze uploaded image for skin tone detection
    """
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        gender = data.get('gender', 'Men')
        session_id = data.get('session_id') or str(uuid.uuid4())
        
        if not image_data:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        # Decode base64 image
        if 'data:image' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save uploaded image
        image_name = f'skin_analysis_{session_id}.jpg'
        image_path = default_storage.save(image_name, ContentFile(image_bytes))
        
        # Analyze skin tone
        detector = SkinToneDetector()
        analysis_result = detector.analyze_skin_tone(image)
        
        if 'error' in analysis_result:
            return JsonResponse({'error': analysis_result['error']}, status=400)
        
        # Save analysis to database
        skin_analysis = SkinToneAnalysis.objects.create(
            session_id=session_id,
            uploaded_image=image_path,
            skin_tone=analysis_result['skin_tone'],
            undertone=analysis_result['undertone'],
            season=analysis_result['season'],
            rgb_values=analysis_result['rgb_avg'],
            hsv_values=analysis_result['hsv_avg']
        )
        
        # Create or get chat session
        chat_session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'gender': gender}
        )
        
        # Generate AI greeting
        try:
            style_agent = StyleAdvisorAgent()
            greeting = style_agent.generate_greeting(
                gender, analysis_result['skin_tone'], analysis_result['season']
            )
        except Exception as e:
            print(f"AI greeting error: {e}")
            # Fallback greeting
            skin_tone_display = analysis_result['skin_tone'].replace('_', ' ')
            greeting = f"Hello! I'm your AI Style Advisor. I've analyzed your skin tone and found that you have beautiful {skin_tone_display} undertones, perfect for {analysis_result['season']} colors! I'm excited to help you find the perfect interview outfits that will make you look confident and professional. Let me show you some amazing options!"
        
        # Add greeting to chat history
        chat_session.add_message('assistant', greeting)
        
        return JsonResponse({
            'success': True,
            'session_id': session_id,
            'analysis': {
                'skin_tone': analysis_result['skin_tone'],
                'undertone': analysis_result['undertone'],
                'season': analysis_result['season'],
                'confidence': analysis_result['confidence']
            },
            'greeting': greeting
        })
        
    except Exception as e:
        print(f"Error in skin tone analysis: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': 'Failed to analyze skin tone'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_recommendations(request):
    """
    Get clothing recommendations based on skin tone analysis
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        print(f"DEBUG: Received session_id: {session_id}")
        
        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)
        
        # Get skin tone analysis
        try:
            skin_analysis = SkinToneAnalysis.objects.get(session_id=session_id)
            chat_session = ChatSession.objects.get(session_id=session_id)
            print(f"DEBUG: Found session - skin_tone: {skin_analysis.skin_tone}, gender: {chat_session.gender}")
        except (SkinToneAnalysis.DoesNotExist, ChatSession.DoesNotExist):
            print(f"DEBUG: Session not found. Available sessions: {list(SkinToneAnalysis.objects.values_list('session_id', flat=True))}")
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Get user preferences
        user_feedback = UserPreference.objects.filter(session_id=session_id)
        preference_agent = PreferenceAgent()
        user_preferences = preference_agent.analyze_preferences(
            [{'liked': pref.liked, 'color': pref.color, 'brand': pref.brand, 'category': pref.category} 
             for pref in user_feedback]
        )
        
        # Get color recommendations
        detector = SkinToneDetector()
        recommended_colors = detector.get_interview_appropriate_colors(skin_analysis.season)
        
        # Get fashion recommendations
        fashion_manager = FashionDatasetManager()
        print(f"DEBUG: Getting recommendations for gender={chat_session.gender}, colors={recommended_colors}, season={skin_analysis.season}")
        
        # Ensure we have fallback colors if recommended_colors is empty
        if not recommended_colors:
            recommended_colors = ['Navy', 'Black', 'White', 'Grey', 'Blue']
            print(f"DEBUG: Using fallback colors: {recommended_colors}")
        
        outfits = fashion_manager.get_recommendations(
            gender=chat_session.gender,
            recommended_colors=recommended_colors,
            season=skin_analysis.season,
            user_preferences=user_preferences,
            limit=5
        )
        
        print(f"DEBUG: Found {len(outfits)} outfits")
        
        # If no outfits found, try with broader criteria
        if not outfits:
            print(f"DEBUG: No outfits found with specific criteria, trying broader search...")
            # Try with just gender and basic professional colors
            outfits = fashion_manager.get_recommendations(
                gender=chat_session.gender,
                recommended_colors=['Navy', 'Black', 'White', 'Grey', 'Blue', 'Brown'],
                season='winter',  # Default season
                user_preferences={},
                limit=5
            )
            print(f"DEBUG: Broader search found {len(outfits)} outfits")
        
        if not outfits:
            print(f"DEBUG: Still no outfits found - dataset size: {len(fashion_manager.df)}")
            # Return a helpful error message with suggestions
            return JsonResponse({
                'error': 'No suitable outfits found',
                'suggestion': 'Please try uploading a different photo or check your internet connection.',
                'debug_info': {
                    'dataset_size': len(fashion_manager.df),
                    'gender': chat_session.gender,
                    'colors_tried': recommended_colors
                }
            }, status=404)
        
        # Generate AI explanations and compliments
        try:
            style_agent = StyleAdvisorAgent()
            enhanced_outfits = []
            
            for outfit in outfits[:3]:  # Show top 3 recommendations
                try:
                    explanation = style_agent.generate_outfit_explanation(
                        outfit, skin_analysis.skin_tone, skin_analysis.season, chat_session.gender
                    )
                    compliment = style_agent.generate_compliment(outfit, chat_session.gender)
                except Exception as ai_error:
                    print(f"AI generation error: {ai_error}")
                    # Fallback explanations
                    explanation = f"This outfit complements your {skin_analysis.season} coloring beautifully and creates a professional, polished look perfect for interviews."
                    compliment = "You'll look confident and professional in this outfit!"
                
                enhanced_outfit = {
                    **outfit,
                    'explanation': explanation,
                    'compliment': compliment
                }
                enhanced_outfits.append(enhanced_outfit)
        except Exception as agent_error:
            print(f"Style agent initialization error: {agent_error}")
            # Use outfits without AI enhancements
            enhanced_outfits = outfits[:3]
        
        # Generate AI message with conversational tone as specified
        skin_tone_display = skin_analysis.skin_tone.replace('_', ' ')
        ai_message = f"Hey there! I've analyzed your skin tone and found that you're a {skin_tone_display} ({skin_analysis.season} season). Here are {len(enhanced_outfits)} professional outfits that'll make you shine at your interview!"
        
        # Add message and recommendations to chat session
        chat_session.add_message('assistant', ai_message, enhanced_outfits)
        
        # Sanitize all data before JSON response to prevent NaN errors
        def sanitize_for_json(obj):
            if isinstance(obj, dict):
                return {k: sanitize_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_for_json(item) for item in obj]
            elif obj is None or str(obj).lower() == 'nan':
                return ''
            else:
                return obj
        
        clean_outfits = sanitize_for_json(enhanced_outfits)
        
        return JsonResponse({
            'success': True,
            'recommendations': clean_outfits,
            'message': ai_message,
            'skin_info': {
                'skin_tone': skin_analysis.skin_tone,
                'season': skin_analysis.season,
                'undertone': skin_analysis.undertone
            }
        })
        
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'error': 'Failed to get recommendations', 
            'details': str(e),
            'success': False
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_feedback(request):
    """
    Submit user feedback (like/dislike) for outfit recommendations
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        outfit_id = data.get('outfit_id')
        liked = data.get('liked')  # True for like, False for dislike
        
        if not all([session_id, outfit_id, liked is not None]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get chat session and current recommendations
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
            skin_analysis = SkinToneAnalysis.objects.get(session_id=session_id)
        except (ChatSession.DoesNotExist, SkinToneAnalysis.DoesNotExist):
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Find the outfit in current recommendations
        outfit = None
        for rec in chat_session.current_recommendations:
            if rec.get('outfit_id') == outfit_id:
                outfit = rec
                break
        
        if not outfit:
            return JsonResponse({'error': 'Outfit not found'}, status=404)
        
        # Save feedback for each item in the outfit
        for item in outfit['items']:
            UserPreference.objects.update_or_create(
                session_id=session_id,
                product_id=f"{outfit_id}_{item['category']}",
                defaults={
                    'liked': liked,
                    'color': item['color'],
                    'category': item['category'],
                    'brand': item['brand']
                }
            )
        
        # Generate AI response
        style_agent = StyleAdvisorAgent()
        preference_agent = PreferenceAgent()
        
        # Get updated preferences
        user_feedback = UserPreference.objects.filter(session_id=session_id)
        user_preferences = preference_agent.analyze_preferences(
            [{'liked': pref.liked, 'color': pref.color, 'brand': pref.brand, 'category': pref.category} 
             for pref in user_feedback]
        )
        
        feedback_response = style_agent.generate_feedback_response(
            'like' if liked else 'dislike',
            user_preferences,
            skin_analysis.skin_tone,
            skin_analysis.season,
            chat_session.gender
        )
        
        # Add personalized preference message
        preference_message = preference_agent.generate_personalized_message(user_preferences)
        
        full_response = f"{feedback_response} {preference_message}"
        chat_session.add_message('assistant', full_response)
        
        response_data = {
            'success': True,
            'message': full_response
        }
        
        # If disliked, offer alternatives
        if not liked:
            fashion_manager = FashionDatasetManager()
            avoided_colors = [item['color'] for item in outfit['items']]
            
            alternatives = fashion_manager.get_alternative_recommendations(
                chat_session.gender, avoided_colors, skin_analysis.season, limit=2
            )
            
            if alternatives:
                enhanced_alternatives = []
                for alt_outfit in alternatives:
                    explanation = style_agent.generate_outfit_explanation(
                        alt_outfit, skin_analysis.skin_tone, skin_analysis.season, chat_session.gender
                    )
                    compliment = style_agent.generate_compliment(alt_outfit, chat_session.gender)
                    
                    enhanced_alternatives.append({
                        **alt_outfit,
                        'explanation': explanation,
                        'compliment': compliment
                    })
                
                response_data['alternatives'] = enhanced_alternatives
                alternative_message = "Here are some alternative options that might be more your style:"
                chat_session.add_message('assistant', alternative_message, enhanced_alternatives)
                response_data['alternative_message'] = alternative_message
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': 'Failed to submit feedback'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_chat_history(request):
    """
    Get chat conversation history for a session
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)
        
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        return JsonResponse({
            'success': True,
            'conversation_history': chat_session.conversation_history,
            'current_recommendations': chat_session.current_recommendations
        })
        
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return JsonResponse({'error': 'Failed to get chat history'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def end_session(request):
    """
    End the styling session with a motivational message
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        if not session_id:
            return JsonResponse({'error': 'Session ID required'}, status=400)
        
        try:
            chat_session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
        
        # Count total outfits shown
        total_outfits = len(chat_session.current_recommendations)
        
        # Generate final motivational message
        style_agent = StyleAdvisorAgent()
        final_message = style_agent.generate_final_motivation(
            chat_session.gender, total_outfits
        )
        
        chat_session.add_message('assistant', final_message)
        
        return JsonResponse({
            'success': True,
            'final_message': final_message
        })
        
    except Exception as e:
        print(f"Error ending session: {str(e)}")
        return JsonResponse({'error': 'Failed to end session'}, status=500)
