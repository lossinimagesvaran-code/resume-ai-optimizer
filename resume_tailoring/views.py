import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import TailoredResume
from .forms import ResumeCustomizationForm
from .utils import generate_tailored_resume, apply_template_formatting, save_resume_as_pdf
from resume_analysis.models import ResumeAnalysis

def tailoring_home(request):
    """Main resume tailoring page - SESSION PERSISTENCE FIX"""
    # Clear previous template selection EVERY time
    if 'tailoring_options' in request.session:
        del request.session['tailoring_options']
    
    # Also clear any individual template keys
    session_keys_to_remove = ['selected_template', 'template_choice', 'last_template']
    for key in session_keys_to_remove:
        if key in request.session:
            del request.session[key]
    
    # Force session save
    request.session.modified = True
    
    # Get recent resume analysis
    recent_analysis = ResumeAnalysis.objects.first()
    
    if not recent_analysis:
        messages.warning(request, 'Please add your resume and job description first to use the Resume Tailoring feature.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        # Get template choice directly from POST data
        template_choice = request.POST.get('template_choice')
        
        # Validate template choice
        valid_templates = ['traditional', 'modern', 'hybrid']
        if template_choice in valid_templates:
            # Store in session with clear naming and timestamp
            request.session['tailoring_options'] = {
                'template_choice': template_choice,
                'timestamp': str(timezone.now()),
                'user_selected': True  # Flag to indicate user actually selected this
            }
            request.session.modified = True
            return redirect('resume_tailoring:customize')
        else:
            messages.error(request, f'Invalid template selection: {template_choice}. Please choose Traditional, Modern, or Hybrid.')
    
    context = {
        'recent_analysis': recent_analysis,
    }
    
    # Set headers to prevent caching
    response = render(request, 'resume_tailoring/home.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def customize_resume(request):
    """Customize the tailored resume"""
    tailoring_options = request.session.get('tailoring_options', {})
    if not tailoring_options:
        messages.error(request, 'Please select a template first.')
        return redirect('resume_tailoring:home')
    
    # Clear any old simplified values from session
    if tailoring_options.get('template_choice') == 'simplified':
        del request.session['tailoring_options']
        messages.error(request, 'Invalid template selection. Please choose a valid template.')
        return redirect('resume_tailoring:home')
    
    # Check if resume analysis exists in session or database
    session_analysis = request.session.get('resume_analysis')
    recent_analysis = ResumeAnalysis.objects.first()
    
    if not session_analysis and not recent_analysis:
        messages.error(request, 'Please analyze your resume first before tailoring.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        form = ResumeCustomizationForm(request.POST)
        if form.is_valid():
            # Generate tailored resume
            try:
                # Use session data if available, otherwise database
                resume_text = session_analysis['resume_text'] if session_analysis else recent_analysis.resume_text
                job_description = session_analysis['job_description'] if session_analysis else recent_analysis.job_description
                
                # Get the selected template - NO FALLBACK
                selected_template = tailoring_options.get('template_choice')
                if not selected_template:
                    messages.error(request, 'Template selection is required. Please go back and select a template.')
                    return redirect('resume_tailoring:home')
                
                # Validate template is still valid
                valid_templates = ['traditional', 'modern', 'hybrid']
                if selected_template not in valid_templates:
                    messages.error(request, f'Invalid template in session: {selected_template}. Please select a new template.')
                    return redirect('resume_tailoring:home')
                
                
                tailored_content = generate_tailored_resume(
                    resume_text=resume_text,
                    job_description=job_description,
                    template_name=selected_template,
                    custom_skills=form.cleaned_data.get('custom_skills', ''),
                    remove_sections=form.cleaned_data.get('remove_sections', []),
                    additional_notes=form.cleaned_data.get('additional_notes', '')
                )
                
                
                # Save tailored resume
                tailored_resume = TailoredResume.objects.create(
                    user=None,  
                    original_resume=resume_text,
                    job_description=job_description,
                    tailored_content=tailored_content if isinstance(tailored_content, str) else str(tailored_content),
                    template_used=selected_template,
                    match_score=session_analysis.get('match_score', 75) if session_analysis else (recent_analysis.match_score if hasattr(recent_analysis, 'match_score') else 75)
                )
                
                
                # Clear session data after successful generation
                if 'tailoring_options' in request.session:
                    del request.session['tailoring_options']
                
                messages.success(request, 'Resume tailored successfully!')
                return redirect('resume_tailoring:preview', resume_id=tailored_resume.id)
                
            except Exception as e:
                messages.error(request, f'Error generating tailored resume: {str(e)}')
                return redirect('resume_tailoring:home')
    else:
        form = ResumeCustomizationForm()
    
    context = {
        'form': form,
        'tailoring_options': tailoring_options,
        'recent_analysis': recent_analysis,
    }
    return render(request, 'resume_tailoring/customize.html', context)

def reset_template(request):
    """Force reset template selection"""
    if 'tailoring_options' in request.session:
        del request.session['tailoring_options']
    
    messages.info(request, 'Template selection has been reset.')
    return redirect('resume_tailoring:home')

def reset_session(request):
    """Completely reset the session for template selection"""
    # Clear all template-related session data
    session_keys = ['tailoring_options', 'selected_template', 'template_choice', 'last_template']
    
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    
    request.session.modified = True
    messages.info(request, 'Session has been reset. Please select a template again.')
    return redirect('resume_tailoring:home')

def download_edited_resume(request, resume_id):
    """Download PDF with edited content"""
    if request.method == 'POST':
        edited_content = request.POST.get('edited_content', '')
        
        try:
            import tempfile
            import os
            from django.http import HttpResponse
            from .utils import save_resume_as_pdf
            
            # Clean the content before PDF generation
            from .utils import clean_resume_content
            cleaned_content = clean_resume_content(edited_content)
            
            # Generate PDF in memory (no temp file needed)
            pdf_data = save_resume_as_pdf(cleaned_content, None)
            
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="tailored_resume_edited.pdf"'
            
            return response
                
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('resume_tailoring:preview', resume_id=resume_id)
    
    return redirect('resume_tailoring:preview', resume_id=resume_id)

def resume_history(request):
    """View resume tailoring history"""
    tailored_resumes = TailoredResume.objects.all().order_by('-created_at')
    
    context = {
        'tailored_resumes': tailored_resumes,
    }
    
    return render(request, 'resume_tailoring/history.html', context)

def preview_resume(request, resume_id):
    """Preview the tailored resume"""
    try:
        tailored_resume = TailoredResume.objects.get(id=resume_id)
    except TailoredResume.DoesNotExist:
        messages.error(request, 'Tailored resume not found.')
        return redirect('resume_tailoring:home')
    
    # Clean the resume content for display
    from .utils import clean_resume_content
    cleaned_content = clean_resume_content(tailored_resume.tailored_content)
    
    context = {
        'tailored_resume': tailored_resume,
        'cleaned_content': cleaned_content,
    }
    return render(request, 'resume_tailoring/preview.html', context)

def edit_resume(request, resume_id):
    """Edit the tailored resume content"""
    try:
        tailored_resume = TailoredResume.objects.get(id=resume_id)
    except TailoredResume.DoesNotExist:
        messages.error(request, 'Tailored resume not found.')
        return redirect('resume_tailoring:home')
    
    if request.method == 'POST':
        new_content = request.POST.get('tailored_content', '')
        if new_content:
            tailored_resume.tailored_content = new_content
            tailored_resume.save()
            messages.success(request, 'Resume updated successfully!')
        else:
            messages.error(request, 'Resume content cannot be empty.')
    
    return redirect('resume_tailoring:preview', resume_id=resume_id)

def download_resume(request, resume_id, format_type):
    """Download the tailored resume in different formats"""
    try:
        tailored_resume = TailoredResume.objects.get(id=resume_id)
    except TailoredResume.DoesNotExist:
        messages.error(request, 'Tailored resume not found.')
        return redirect('resume_tailoring:home')
    
    if format_type == 'txt':
        response = HttpResponse(tailored_resume.tailored_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="tailored_resume_{tailored_resume.template_used}.txt"'
        return response
    
    elif format_type == 'pdf':
        try:
            # Apply template formatting before PDF generation
            formatted_content = apply_template_formatting(tailored_resume.tailored_content, tailored_resume.template_used)
            pdf_content = save_resume_as_pdf(formatted_content, None)
                
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="tailored_resume_{tailored_resume.template_used}.pdf"'
            return response
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('resume_tailoring:preview', resume_id=resume_id)
    
    else:
        messages.error(request, 'Invalid format specified.')
        return redirect('resume_tailoring:preview', resume_id=resume_id)

def tailoring_history(request):
    """Display user's tailoring history"""
    tailored_resumes = TailoredResume.objects.all()
    context = {
        'tailored_resumes': tailored_resumes,
    }
    return render(request, 'resume_tailoring/history.html', context)

@csrf_exempt
def api_generate_resume(request):
    """API endpoint for generating tailored resume"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        template_name = data.get('template_name', 'traditional')
        
        if not resume_text or not job_description:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Generate tailored resume
        tailored_content = generate_tailored_resume(
            resume_text=resume_text,
            job_description=job_description,
            template_name=template_name
        )
        
        return JsonResponse({
            'tailored_content': tailored_content,
            'template_used': template_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


