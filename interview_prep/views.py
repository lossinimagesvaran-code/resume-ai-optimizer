import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .forms import InterviewQuestionForm, TipCompletionForm, InterviewPrepForm
from .models import InterviewTip, InterviewChat, InterviewSession
from .utils import generate_interview_tips, generate_interview_answer
from resume_analysis.models import ResumeAnalysis
from django.utils import timezone
from datetime import timedelta

def interview_prep_home(request):
    """Interview preparation home page"""
    # FORCE COMPLETE SESSION CLEARING
    keys_to_clear = ['interview_data', 'interview_tips', 'interview_chat_history', 'interview_session_active', 'interview_form_data', 'interview_content']
    for key in keys_to_clear:
        request.session.pop(key, None)
    request.session.flush()  # Complete session flush
    request.session.create()  # Create new session
    
    # Check if user has completed resume analysis (any analysis, not just recent)
    recent_analysis = ResumeAnalysis.objects.order_by('-created_at').first()
    
    # Also check session for analysis data
    has_session_analysis = (
        request.session.get('has_recent_analysis') or 
        request.session.get('latest_analysis_id') or
        request.session.get('resume_analysis_data')
    )
    
    if not recent_analysis and not has_session_analysis:
        messages.warning(
            request, 
            'Please add your resume and job description first to use the Interview Preparation. '
            'Complete the resume analysis to get personalized interview tips.'
        )
        return redirect('resume_analysis:home')
    
    # Set new session as active
    request.session['interview_session_active'] = True
    request.session.modified = True
    
    context = {
        'recent_analysis': recent_analysis,
    }
    return render(request, 'interview_prep/home.html', context)

def interview_home(request):
    """Interview preparation home page"""
    # Check if resume analysis exists in session or database
    session_analysis = request.session.get('resume_analysis')
    recent_analysis = ResumeAnalysis.objects.first()
    
    if not session_analysis and not recent_analysis:
        messages.error(request, 'Please analyze your resume first before generating interview tips.')
        return redirect('resume_analysis:home')
    
    # Clear old tips when starting new session
    if 'clear_tips' in request.GET:
        InterviewTip.objects.filter(user=None).delete()
        return redirect('interview_prep:home')
    
    # Get current tips by level
    level_1_tips = InterviewTip.objects.filter(user=None, level=1).order_by('id')
    level_2_tips = InterviewTip.objects.filter(user=None, level=2).order_by('id')
    level_3_tips = InterviewTip.objects.filter(user=None, level=3).order_by('id')
    
    # Check if levels are complete (all tips checked)
    level_1_complete = level_1_tips.exists() and all(tip.is_completed for tip in level_1_tips)
    level_2_complete = level_2_tips.exists() and all(tip.is_completed for tip in level_2_tips)
    
    # Check if level 3 is complete for congratulations
    level_3_complete = level_3_tips.exists() and all(tip.is_completed for tip in level_3_tips)
    
    # Determine current level and next action
    if not level_1_tips.exists():
        current_level = 1
        next_action = "Generate Level 1 Tips"
        show_unlock_button = False
    elif level_3_complete:
        current_level = 3
        next_action = "Congratulations! Good luck with your interview!"
        show_unlock_button = False
        messages.success(request, "🎉 Congratulations! You've completed all interview preparation levels. Good luck with your interview!")
    else:
        current_level = 1 if not level_1_complete else (2 if not level_2_complete else 3)
        next_action = "Check off all current level tips to unlock the next level."
        show_unlock_button = False
    
    # Calculate tips completed count
    all_tips = list(level_1_tips) + list(level_2_tips) + list(level_3_tips)
    completed_tips = [tip for tip in all_tips if tip.is_completed]
    tips_completed_count = f"{len(completed_tips)}/{len(all_tips)}" if all_tips else "0/0"
    
    context = {
        'recent_analysis': recent_analysis,
        'level_1_tips': level_1_tips,
        'level_2_tips': level_2_tips,
        'level_3_tips': level_3_tips,
        'level_1_complete': level_1_complete,
        'level_2_complete': level_2_complete,
        'level_3_complete': level_3_complete,
        'current_level': current_level,
        'next_action': next_action,
        'show_unlock_button': show_unlock_button,
        'unlock_level': unlock_level if 'unlock_level' in locals() else None,
        'tips_completed_count': tips_completed_count,
    }
    return render(request, 'interview_prep/home.html', context)

def generate_tips(request):
    """Generate interview tips for level 1 only"""
    # Check if resume analysis exists in session or database
    session_analysis = request.session.get('resume_analysis')
    recent_analysis = ResumeAnalysis.objects.first()
    
    if not session_analysis and not recent_analysis:
        messages.error(request, 'Please analyze your resume first before generating interview tips.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        try:
            # Only generate Level 1 tips
            level_1_tips = InterviewTip.objects.filter(user=None, level=1)
            
            if level_1_tips.exists():
                messages.warning(request, 'Level 1 tips already exist. Complete them to unlock next level.')
                return redirect('interview_prep:home')
            
            # Get resume and job description from session or database
            resume_text = session_analysis['resume_text'] if session_analysis else recent_analysis.resume_text
            job_description = session_analysis['job_description'] if session_analysis else recent_analysis.job_description
            
            # Generate interview tips using AI
            tips_list = generate_interview_tips(
                resume_text=resume_text,
                job_description=job_description,
                level=1,
                experience_level='mid',
                industry=''
            )
            
            # Create individual InterviewTip objects
            tips_created = []
            if isinstance(tips_list, list):
                for i, tip in enumerate(tips_list[:5]):  # Limit to 5 tips
                    interview_tip = InterviewTip.objects.create(
                        user=None,
                        level=1,
                        tip_content=str(tip).strip(),
                        is_completed=False
                    )
                    tips_created.append(interview_tip)
            else:
                # Handle single tip case
                interview_tip = InterviewTip.objects.create(
                    user=None,
                    level=1,
                    tip_content=str(tips_list).strip(),
                    is_completed=False
                )
                tips_created.append(interview_tip)
            
            messages.success(request, f'Level 1 interview tips generated successfully! ({len(tips_created)} tips created)')
            return redirect('interview_prep:home')
            
        except Exception as e:
            messages.error(request, f'Error generating tips: {str(e)}')
    
    return redirect('interview_prep:home')

def unlock_level(request):
    """Unlock next level tips"""
    # Check if resume analysis exists in session or database
    session_analysis = request.session.get('resume_analysis')
    recent_analysis = ResumeAnalysis.objects.first()
    
    if not session_analysis and not recent_analysis:
        messages.error(request, 'Please analyze your resume first.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        try:
            level = int(request.POST.get('level', 2))
            
            # Get resume and job description from session or database
            resume_text = session_analysis['resume_text'] if session_analysis else recent_analysis.resume_text
            job_description = session_analysis['job_description'] if session_analysis else recent_analysis.job_description
            
            # Generate interview tips using AI
            tips_list = generate_interview_tips(
                resume_text=resume_text,
                job_description=job_description,
                level=level,
                experience_level='mid',
                industry=''
            )
            
            # Create individual InterviewTip objects
            tips_created = []
            if isinstance(tips_list, list):
                for i, tip in enumerate(tips_list[:5]):  # Limit to 5 tips
                    interview_tip = InterviewTip.objects.create(
                        user=None,
                        level=level,
                        tip_content=str(tip).strip(),
                        is_completed=False
                    )
                    tips_created.append(interview_tip)
            else:
                # Handle single tip case
                interview_tip = InterviewTip.objects.create(
                    user=None,
                    level=level,
                    tip_content=str(tips_list).strip(),
                    is_completed=False
                )
                tips_created.append(interview_tip)
            
            messages.success(request, f'Level {level} interview tips unlocked! ({len(tips_created)} tips created)')
            return redirect('interview_prep:home')
            
        except Exception as e:
            messages.error(request, f'Error unlocking level: {str(e)}')
    
    return redirect('interview_prep:home')

def interview_coach_chat(request):
    """Interview coach chat interface"""
    # Get user's recent resume analysis
    recent_analysis = ResumeAnalysis.objects.first()
    
    # Check if resume analysis exists, redirect if not
    if not recent_analysis:
        messages.warning(request, 'Please add your resume and job description first to use the Interview Preparation feature.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        form = InterviewQuestionForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            
            try:
                # Generate AI answer
                answer = generate_interview_answer(
                    question=question,
                    resume_text=recent_analysis.resume_text,
                    job_description=recent_analysis.job_description
                )
                
                # Save chat
                InterviewChat.objects.create(
                    user=None,  # No user authentication required
                    question=question,
                    answer=answer
                )
                
                messages.success(request, 'Answer generated successfully!')
                return redirect('interview_prep:chat')
                
            except Exception as e:
                messages.error(request, f'Error generating answer: {str(e)}')
    else:
        form = InterviewQuestionForm()
    
    # Get chat history
    chat_history = InterviewChat.objects.all()[:20]  # Last 20 chats
    
    context = {
        'form': form,
        'chat_history': chat_history,
        'recent_analysis': recent_analysis,
    }
    return render(request, 'interview_prep/chat.html', context)

def mark_tip_completed(request, tip_id):
    """Mark a tip as completed"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            is_completed = data.get('is_completed', False)
            
            tip = InterviewTip.objects.get(id=tip_id)
            tip.is_completed = is_completed
            tip.save()
            
            return JsonResponse({
                'success': True,
                'is_completed': tip.is_completed,
            })
            
        except InterviewTip.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Tip not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})

def unlock_next_level(request):
    """Unlock the next level of tips"""
    session = InterviewSession.objects.order_by('-session_started').first()
    
    if not session:
        messages.error(request, 'No active session found. Please generate tips first.')
        return redirect('interview_prep:home')
    
    if session.current_level < 3 and session.tips_completed >= session.total_tips:
        # Get recent analysis for generating next level tips
        recent_analysis = ResumeAnalysis.objects.order_by('-created_at').first()
        
        if not recent_analysis:
            messages.error(request, 'Resume analysis required to generate next level tips.')
            return redirect('resume_analysis:home')
        
        try:
            # Generate next level tips
            next_level = session.current_level + 1
            tips_list = generate_interview_tips(
                resume_text=recent_analysis.resume_text,
                job_description=recent_analysis.job_description,
                level=next_level,
                experience_level=session.experience_level,
                industry=session.company_name
            )
            
            # Create new tips for next level
            tips_created = []
            if isinstance(tips_list, list):
                for tip in tips_list[:5]:  # Limit to 5 tips per level
                    interview_tip = InterviewTip.objects.create(
                        user=None,
                        level=next_level,
                        tip_content=str(tip).strip(),
                        is_completed=False
                    )
                    tips_created.append(interview_tip)
            
            # Update session to next level
            session.current_level = next_level
            session.tips_completed = 0
            session.total_tips = len(tips_created)
            session.save()
            
            messages.success(request, f'Level {next_level} unlocked! {len(tips_created)} new tips generated.')
            
        except Exception as e:
            messages.error(request, f'Error generating next level tips: {str(e)}')
    else:
        messages.warning(request, 'Complete all current level tips to unlock the next level.')
    
    return redirect('interview_prep:home')

def download_all_tips(request):
    """Download all completed tips as a combined document"""
    try:
        from fpdf import FPDF
        
        # Get all completed tips
        completed_tips = InterviewTip.objects.filter(user=None, is_completed=True).order_by('level')
        
        if not completed_tips:
            messages.warning(request, 'No completed tips to download.')
            return redirect('interview_prep:home')
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Interview Preparation Tips", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        
        for tip in completed_tips:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"Level {tip.level} Tip", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, tip.tip_content)
            pdf.ln(5)
        
        # Return PDF response
        from django.http import HttpResponse
        response = HttpResponse(pdf.output(dest='S').encode('latin-1'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="interview_tips.pdf"'
        return response
        
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('interview_prep:home')

def clear_chat_history(request):
    """Clear chat history"""
    if request.method == 'POST':
        InterviewChat.objects.all().delete()
        # FORCE COMPLETE SESSION CLEARING
        keys_to_clear = ['interview_data', 'interview_tips', 'interview_chat_history', 'interview_session_active', 'interview_form_data', 'interview_content']
        for key in keys_to_clear:
            request.session.pop(key, None)
        request.session.flush()
        request.session.clear()
        request.session.modified = True
        messages.success(request, 'Chat history and session data cleared successfully!')
    
    return redirect('interview_prep:chat')

@csrf_exempt
def api_generate_tips(request):
    """API endpoint for generating interview tips"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        level = data.get('level', 1)
        
        tips = generate_interview_tips(
            resume_text=resume_text,
            job_description=job_description,
            level=level
        )
        
        return JsonResponse({
            'tips': tips,
            'level': level
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_chat_answer(request):
    """API endpoint for getting chat answers"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)
        
        answer = generate_interview_answer(
            question=question,
            resume_text=resume_text,
            job_description=job_description
        )
        
        return JsonResponse({
            'answer': answer,
            'question': question
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

