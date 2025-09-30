import json
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from .forms import CoverLetterForm, CoverLetterCustomizationForm
from .models import CoverLetter
from .utils import generate_cover_letter_with_ai, save_cover_letter_as_pdf
from resume_analysis.models import ResumeAnalysis
from django.utils import timezone
from datetime import timedelta
import uuid

def cover_letter_home(request):
    """Cover letter generation home page"""
    # AGGRESSIVE SESSION CLEARING - Clear everything related to cover letters
    import time
    
    # Clear all possible cover letter keys
    keys_to_clear = [
        'cover_letter_data', 'cover_letter_session_id', 'cover_letter_content', 
        'cover_letter_form_data', 'cover_letter_generated', 'cover_letter_preview',
        'cl_data', 'cl_session', 'cl_content', 'cl_form'
    ]
    
    for key in list(request.session.keys()):
        if 'cover' in key.lower() or 'letter' in key.lower():
            request.session.pop(key, None)
    
    for key in keys_to_clear:
        request.session.pop(key, None)
    
    # Multiple clearing methods
    request.session.flush()
    request.session.clear()
    request.session.cycle_key()
    request.session.modified = True
    
    # Force new session creation
    time.sleep(0.1)  # Small delay to ensure clearing
    
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
            'Please add your resume and job description first to use the Cover Letter Generator. '
            'Complete the resume analysis to get personalized cover letters.'
        )
        return redirect('resume_analysis:home')
    
    # Generate a unique session ID for this cover letter session
    session_id = str(uuid.uuid4())
    request.session['cover_letter_session_id'] = session_id
    request.session.modified = True
    
    if request.method == 'POST':
        form = CoverLetterForm(request.POST)
        if form.is_valid():
            # COMPLETE SESSION CLEARING on home page load
            request.session.flush()
            request.session.clear()
            
            # Preserve only essential session data
            request.session['has_recent_analysis'] = True
            request.session['latest_analysis_id'] = recent_analysis.id if recent_analysis else None
            request.session.modified = True
            
            # Clear any existing data first
            keys_to_clear = [
                'cover_letter_data', 'cover_letter_session_id', 'cover_letter_content', 
                'cover_letter_form_data', 'cover_letter_generated', 'cover_letter_preview'
            ]
            for key in keys_to_clear:
                request.session.pop(key, None)
            # Store NEW form data in session
            request.session['cover_letter_data'] = form.cleaned_data
            request.session.modified = True
            return redirect('cover_letter:generate')
    else:
        # Always create empty form - no pre-filling to ensure clean session
        form = CoverLetterForm()
    
    context = {
        'form': form,
        'recent_analysis': recent_analysis,
    }
    return render(request, 'cover_letter/home.html', context)

def generate_cover_letter(request):
    """Generate the cover letter using AI"""
    cover_letter_data = request.session.get('cover_letter_data')
    if not cover_letter_data:
        messages.error(request, 'Please fill out the cover letter form first.')
        return redirect('cover_letter:home')
    
    # Check if resume analysis exists in session or database
    session_analysis = request.session.get('resume_analysis')
    recent_analysis = ResumeAnalysis.objects.order_by('-created_at').first()
    
    if not session_analysis and not recent_analysis:
        messages.error(request, 'Please analyze your resume first before generating cover letter.')
        return redirect('resume_analysis:home')
    
    if request.method == 'POST':
        form = CoverLetterCustomizationForm(request.POST)
        if form.is_valid():
            # Generate cover letter
            try:
                # Use session data if available, otherwise database
                resume_text = session_analysis['resume_text'] if session_analysis else recent_analysis.resume_text
                job_description = session_analysis['job_description'] if session_analysis else recent_analysis.job_description
                
                cover_letter_content = generate_cover_letter_with_ai(
                    personal_info=cover_letter_data,
                    company_info={
                        'name': cover_letter_data['company_name'],
                        'address': cover_letter_data.get('company_address', ''),
                        'job_title': cover_letter_data['job_title']
                    },
                    resume_text=resume_text,
                    job_description=job_description,
                    writing_style=cover_letter_data['writing_style'],
                    focus_areas=cover_letter_data.get('focus_areas', []),
                    additional_notes=cover_letter_data.get('additional_notes', '')
                )
                
                # Save cover letter
                cover_letter = CoverLetter.objects.create(
                    user=None,  # No user authentication required
                    job_title=cover_letter_data['job_title'],
                    company_name=cover_letter_data['company_name'],
                    cover_letter_content=cover_letter_content,
                    personal_info=cover_letter_data  # Store all personal info as JSON
                )
                
                # FORCE COMPLETE SESSION CLEARING after generation
                keys_to_clear = ['cover_letter_data', 'cover_letter_session_id', 'cover_letter_content', 'cover_letter_form_data']
                for key in keys_to_clear:
                    request.session.pop(key, None)
                request.session.flush()  # Complete session flush
                request.session.clear()  # Additional clearing
                request.session.modified = True
                
                messages.success(request, 'Cover letter generated successfully!')
                return redirect('cover_letter:preview', letter_id=cover_letter.id)
                
            except Exception as e:
                messages.error(request, f'Error generating cover letter: {str(e)}')
                return redirect('cover_letter:home')
    else:
        # Pre-fill with generated content
        try:
            generated_content = generate_cover_letter_with_ai(
                personal_info=cover_letter_data,
                company_info={
                    'name': cover_letter_data['company_name'],
                    'address': cover_letter_data.get('company_address', ''),
                    'job_title': cover_letter_data['job_title']
                },
                resume_text=recent_analysis.resume_text,
                job_description=recent_analysis.job_description,
                writing_style=cover_letter_data['writing_style'],
                focus_areas=cover_letter_data.get('focus_areas', []),
                additional_notes=cover_letter_data.get('additional_notes', '')
            )
            
            form = CoverLetterCustomizationForm(initial={
                'custom_content': generated_content
            })
            
        except Exception as e:
            messages.error(request, f'Error generating initial cover letter: {str(e)}')
            return redirect('cover_letter:home')
    
    context = {
        'form': form,
        'cover_letter_data': cover_letter_data,
        'recent_analysis': recent_analysis,
    }
    return render(request, 'cover_letter/generate.html', context)

def preview_cover_letter(request, letter_id):
    """Preview the generated cover letter"""
    # AGGRESSIVE SESSION CLEARING after generation
    keys_to_clear = [
        'cover_letter_data', 'cover_letter_session_id', 'cover_letter_content', 
        'cover_letter_form_data', 'cover_letter_generated', 'cover_letter_preview',
        'cl_data', 'cl_session', 'cl_content', 'cl_form'
    ]
    
    # Clear all cover letter related keys
    for key in list(request.session.keys()):
        if 'cover' in key.lower() or 'letter' in key.lower():
            request.session.pop(key, None)
    
    for key in keys_to_clear:
        request.session.pop(key, None)
    
    # Multiple clearing methods
    request.session.flush()
    request.session.clear()
    request.session.cycle_key()
    request.session.modified = True
    
    try:
        cover_letter = CoverLetter.objects.get(id=letter_id)
    except CoverLetter.DoesNotExist:
        messages.error(request, 'Cover letter not found.')
        return redirect('cover_letter:home')
    
    context = {
        'cover_letter': cover_letter,
    }
    return render(request, 'cover_letter/preview.html', context)

def clear_cover_letter_session(request):
    """Clear cover letter session data"""
    # Complete session destruction
    request.session.flush()
    request.session.clear()
    
    # Create new session
    try:
        request.session.delete()
        request.session.create()
    except:
        pass
    
    # Restore only essential data
    from resume_analysis.models import ResumeAnalysis
    from datetime import timedelta
    from django.utils import timezone
    
    recent_analysis = ResumeAnalysis.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at').first()
    
    if recent_analysis:
        request.session['has_recent_analysis'] = True
        request.session['latest_analysis_id'] = recent_analysis.id
    
    request.session.modified = True
    messages.success(request, 'Cover letter session completely cleared!')
    
    # Return clear form template that will clear browser data
    return render(request, 'cover_letter/clear_form.html')

def download_cover_letter(request, letter_id, format_type):
    """Download the cover letter in different formats"""
    try:
        cover_letter = CoverLetter.objects.get(id=letter_id)
    except CoverLetter.DoesNotExist:
        messages.error(request, 'Cover letter not found.')
        return redirect('cover_letter:home')
    
    # Clean company name for filename
    import re
    safe_company_name = re.sub(r'[^\w\s-]', '', cover_letter.company_name)
    safe_company_name = re.sub(r'[-\s]+', '_', safe_company_name)
    
    if format_type == 'txt':
        response = HttpResponse(cover_letter.cover_letter_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="cover_letter_{safe_company_name}.txt"'
        return response
    
    elif format_type == 'pdf':
        try:
            import tempfile
            import os
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                filename = tmp_file.name
            
            pdf_content = save_cover_letter_as_pdf(cover_letter.cover_letter_content, filename)
            
            # Clean up temp file
            if os.path.exists(filename):
                os.unlink(filename)
                
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cover_letter_{safe_company_name}.pdf"'
            return response
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('cover_letter:preview', letter_id=letter_id)
    
    else:
        messages.error(request, 'Invalid format specified.')
        return redirect('cover_letter:preview', letter_id=letter_id)

def cover_letter_history(request):
    """Display user's cover letter history"""
    cover_letters = CoverLetter.objects.all()
    context = {
        'cover_letters': cover_letters,
    }
    return render(request, 'cover_letter/history.html', context)

def edit_cover_letter(request, letter_id):
    """Edit an existing cover letter"""
    try:
        cover_letter = CoverLetter.objects.get(id=letter_id)
    except CoverLetter.DoesNotExist:
        messages.error(request, 'Cover letter not found.')
        return redirect('cover_letter:history')
    
    if request.method == 'POST':
        form = CoverLetterCustomizationForm(request.POST)
        if form.is_valid():
            cover_letter.cover_letter_content = form.cleaned_data['custom_content']
            cover_letter.save()
            messages.success(request, 'Cover letter updated successfully!')
            return redirect('cover_letter:preview', letter_id=cover_letter.id)
    else:
        form = CoverLetterCustomizationForm(initial={
            'custom_content': cover_letter.cover_letter_content
        })
    
    context = {
        'form': form,
        'cover_letter': cover_letter,
    }
    return render(request, 'cover_letter/edit.html', context)

