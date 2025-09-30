import json
import fitz  # PyMuPDF
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .forms import ResumeUploadForm, JobDescriptionForm
from .models import ResumeAnalysis, ResumeUpload
from .utils import analyze_resume_with_ai

def resume_analysis_home(request):
    """Main resume analysis page"""
    if request.method == 'POST':
        resume_form = ResumeUploadForm(request.POST, request.FILES)
        jd_form = JobDescriptionForm(request.POST)
        
        if resume_form.is_valid() and jd_form.is_valid():
            # Extract text from PDF FIRST (before saving form which consumes file pointer)
            try:
                # Debugging file upload
                # print("=== DEBUGGING FILE UPLOAD ===")
                # print(f"request.FILES keys: {list(request.FILES.keys())}")
                
                if 'resume_file' not in request.FILES:
                    messages.error(request, "No file was uploaded. Please select a PDF file.")
                    return redirect('resume_analysis:home')
                
                uploaded_file = request.FILES['resume_file']
                # print(f"File name: {uploaded_file.name}")
                # print(f"File size: {uploaded_file.size}")
                # print(f"Content type: {uploaded_file.content_type}")
                
                if uploaded_file.size == 0:
                    messages.error(request, "The uploaded file is empty. Please check your file and try again.")
                    return redirect('resume_analysis:home')
                
                # Reset file pointer to beginning
                uploaded_file.seek(0)
                
                # Read file content into memory
                file_content = uploaded_file.read()
                # print(f"File content read: {len(file_content)} bytes")
                
                if len(file_content) == 0:
                    messages.error(request, "Could not read file content. Please try uploading again.")
                    return redirect('resume_analysis:home')
                
                # Open PDF from memory
                doc = fitz.open(stream=file_content, filetype="pdf")
                # print(f"PDF opened successfully, pages: {doc.page_count}")
                
                if doc.page_count == 0:
                    messages.error(request, "The PDF file has no pages.")
                    doc.close()
                    return redirect('resume_analysis:home')
                
                resume_text = ""
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    page_text = page.get_text()
                    resume_text += page_text + "\n"
                    # print(f"Page {page_num + 1} text length: {len(page_text)}")
                
                doc.close()
                
                if not resume_text.strip():
                    messages.error(request, "Could not extract text from the PDF. The file might be a scanned image or password protected.")
                    return redirect('resume_analysis:home')
                
                # print(f"Total extracted text length: {len(resume_text)} characters")
                # print(f"First 200 chars: {resume_text[:200]}")
                
                # Reset file pointer again for form save
                uploaded_file.seek(0)
                
                # Now save the form
                resume_upload = resume_form.save(commit=False)
                resume_upload.user = None  # No user authentication required
                resume_upload.original_filename = uploaded_file.name
                resume_upload.save()
                
            except Exception as e:
                # print(f"PDF processing error: {str(e)}")
                import traceback
                # traceback.print_exc()
                messages.error(request, f"Error processing PDF: {str(e)}. Please ensure you're uploading a valid PDF file.")
                return redirect('resume_analysis:home')
            
            # Get job description
            job_description = jd_form.cleaned_data['job_description']
            
            # Perform AI analysis
            try:
                # print(f"Starting AI analysis for resume length: {len(resume_text)} chars, JD length: {len(job_description)} chars")
                analysis_result = analyze_resume_with_ai(resume_text, job_description)
                # print(f"AI analysis completed: {analysis_result}")
                
                # Save analysis to database
                analysis = ResumeAnalysis.objects.create(
                    user=None,  # No user authentication required
                    resume_text=resume_text,
                    job_description=job_description,
                    analysis_result=analysis_result.get('analysis', 'Analysis completed'),
                    match_score=analysis_result.get('match_score', 50),
                    keywords_found=analysis_result.get('keywords_found', []),
                    missing_skills=analysis_result.get('missing_skills', []),
                    recommendations=analysis_result.get('recommendations', [])
                )
                
                messages.success(request, 'Resume analysis completed successfully!')
                
                # Store comprehensive analysis data in session for other modules
                request.session['resume_analysis'] = {
                    'resume_text': resume_text,
                    'job_description': job_description,
                    'analysis_result': analysis_result,
                    'analysis_id': analysis.id,
                    'created_at': analysis.created_at.isoformat(),
                    'match_score': analysis_result.get('match_score', 50),
                    'keywords_found': analysis_result.get('keywords_found', []),
                    'missing_skills': analysis_result.get('missing_skills', []),
                    'recommendations': analysis_result.get('recommendations', [])
                }
                request.session['has_recent_analysis'] = True
                request.session['analysis_completed'] = True
                request.session.modified = True
                
                return redirect('resume_analysis:results', analysis_id=analysis.id)
                
            except Exception as e:
                # print(f"Error during analysis: {str(e)}")
                import traceback
                # traceback.print_exc()
                messages.error(request, f'Error during analysis: {str(e)}')
                return redirect('resume_analysis:home')
    else:
        resume_form = ResumeUploadForm()
        jd_form = JobDescriptionForm()
    
    context = {
        'resume_form': resume_form,
        'jd_form': jd_form,
    }
    return render(request, 'resume_analysis/home.html', context)

def analysis_results(request, analysis_id):
    """Display analysis results"""
    try:
        analysis = ResumeAnalysis.objects.get(id=analysis_id)
    except ResumeAnalysis.DoesNotExist:
        messages.error(request, 'Analysis not found.')
        return redirect('resume_analysis:home')
    
    context = {
        'analysis': analysis,
    }
    return render(request, 'resume_analysis/results.html', context)

def analysis_history(request):
    """Display user's analysis history"""
    analyses = ResumeAnalysis.objects.all()  # Show all analyses since no user auth
    context = {
        'analyses': analyses,
    }
    return render(request, 'resume_analysis/history.html', context)

@csrf_exempt
def api_analyze_resume(request):
    """API endpoint for resume analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        resume_text = data.get('resume_text', '')
        job_description = data.get('job_description', '')
        
        if not resume_text or not job_description:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Perform analysis
        result = analyze_resume_with_ai(resume_text, job_description)
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

