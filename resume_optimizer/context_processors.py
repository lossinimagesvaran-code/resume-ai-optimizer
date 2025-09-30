from resume_analysis.models import ResumeAnalysis

def navigation_context(request):
    """
    Context processor to ensure navigation access control works properly.
    Features are locked until resume analysis is completed.
    """
    # Only set has_recent_analysis if there's actually a completed analysis
    # AND the user has been through the analysis flow
    
    # Check if user has explicitly completed analysis in this session
    if request.session.get('analysis_completed') and request.session.get('has_recent_analysis'):
        return {}
    
    # Reset the flag - features should be locked by default
    if 'has_recent_analysis' in request.session:
        del request.session['has_recent_analysis']
        request.session.modified = True
    
    return {}
