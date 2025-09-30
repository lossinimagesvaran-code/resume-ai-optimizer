import json
import google.generativeai as genai
from django.conf import settings
from typing import Dict, List

# Configure Gemini AI
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_interview_tips(
    resume_text: str,
    job_description: str,
    level: int = 1,
    focus_areas: List[str] = None,
    experience_level: str = "mid",
    industry: str = ""
) -> List[str]:
    """Generate interview preparation tips based on level and context"""
    
    if focus_areas is None:
        focus_areas = []
    
    level_prompts = {
        1: "Generate 5 essential interview preparation tips. Focus on fundamental preparation, basic technical topics, and essential behavioral questions. Keep each tip concise (1-2 sentences).",
        2: "Generate 5 advanced interview preparation tips. Include company-specific research, situational questions, and intermediate technical deep dives. Keep each tip concise (1-2 sentences).",
        3: "Generate 5 expert-level interview preparation tips. Focus on advanced negotiation strategies, complex technical scenarios, and executive-level preparation. Keep each tip concise (1-2 sentences)."
    }
    
    prompt = f"""
    Based on the resume and job description, generate personalized interview preparation tips.
    
    LEVEL: {level_prompts[level]}
    
    CONTEXT:
    - Experience Level: {experience_level}
    - Industry: {industry if industry else 'General'}
    - Focus Areas: {', '.join(focus_areas) if focus_areas else 'All areas'}
    
    REQUIREMENTS:
    - Keep each tip very concise (1-2 sentences max per tip)
    - Present as actionable, specific advice
    - Consider the user's background from the resume
    - Address the specific job requirements
    - Make tips practical and implementable
    - Return ONLY the tips, one per line
    - Do NOT use JSON format, markdown, or any special characters
    - Do NOT include quotes, brackets, or any formatting symbols
    
    Resume: {resume_text[:800]}
    Job Description: {job_description[:800]}
    
    Return exactly 5 tips, each on a separate line with no formatting.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response text
        response_text = response_text.replace('```json', '').replace('```', '').replace('[', '').replace(']', '')
        response_text = response_text.replace('"', '').replace("'", '').replace(',', '')
        
        # Split by lines and clean up
        tips = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('{') and not line.startswith('}') and len(line) > 10:
                # Remove any remaining JSON artifacts
                line = line.replace('(', '').replace(')', '').replace('```', '')
                tips.append(line)
        
        # Return exactly 5 tips
        return tips[:5] if tips else generate_fallback_tips(level, experience_level, industry)
        
    except Exception as e:
        # Fallback tips if AI fails
        return generate_fallback_tips(level, experience_level, industry)

def generate_fallback_tips(level: int, experience_level: str, industry: str) -> List[str]:
    """Generate fallback tips if AI fails"""
    
    base_tips = {
        1: [
            "Research the company thoroughly - understand their mission, values, and recent news.",
            "Prepare answers to common behavioral questions using the STAR method.",
            "Review your resume and be ready to discuss every bullet point in detail.",
            "Practice your elevator pitch and prepare thoughtful questions to ask the interviewer.",
            "Dress professionally and arrive 10-15 minutes early to the interview location."
        ],
        2: [
            "Analyze the company's competitors and understand their market position.",
            "Prepare specific examples of challenging situations you've handled successfully.",
            "Research the interviewer's background and prepare relevant talking points.",
            "Practice technical questions related to your field and the specific role.",
            "Prepare salary negotiation strategies and research industry compensation ranges."
        ],
        3: [
            "Develop executive presence through confident body language and communication style.",
            "Prepare strategic questions that demonstrate your business acumen and vision.",
            "Research industry trends and prepare insights on future challenges and opportunities.",
            "Practice complex problem-solving scenarios and strategic thinking exercises.",
            "Prepare negotiation strategies for executive compensation and benefits packages."
        ]
    }
    
    return base_tips.get(level, base_tips[1])

def generate_interview_answer(
    question: str,
    resume_text: str,
    job_description: str
) -> str:
    """Generate a concise answer to an interview question"""
    
    prompt = f"""
    You are an expert interview coach. Answer this interview question with practical, actionable advice.
    
    QUESTION: {question}
    
    CONTEXT:
    - User's Resume Background: {resume_text[:500]}
    - Target Job: {job_description[:500]}
    
    REQUIREMENTS:
    - Keep the answer VERY concise (max 3-4 sentences)
    - Provide actionable, practical advice
    - Consider the user's specific background
    - Address the job requirements
    - Be encouraging and constructive
    
    Give direct, practical advice only. No fluff or generic statements.
    """
    
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        # Ensure answer is concise
        if len(answer) > 300:
            sentences = answer.split('.')
            answer = '. '.join(sentences[:3]) + '.'
        
        return answer
        
    except Exception as e:
        # Fallback answer if AI fails
        return generate_fallback_answer(question)

def generate_fallback_answer(question: str) -> str:
    """Generate a fallback answer if AI fails"""
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['weakness', 'weaknesses']):
        return "Choose a real weakness you've actively worked to improve. Explain what you learned and how you've grown from it."
    
    elif any(word in question_lower for word in ['strength', 'strengths']):
        return "Select 2-3 strengths that directly relate to the job requirements. Provide specific examples that demonstrate these strengths."
    
    elif any(word in question_lower for word in ['experience', 'background']):
        return "Focus on relevant experience that matches the job requirements. Use specific examples and quantify achievements when possible."
    
    elif any(word in question_lower for word in ['salary', 'compensation']):
        return "Research industry standards first. Provide a range based on your experience and the role requirements. Be prepared to negotiate."
    
    elif any(word in question_lower for word in ['company', 'organization']):
        return "Research the company thoroughly. Understand their mission, values, recent news, and how your role contributes to their goals."
    
    else:
        return "Prepare a concise, specific answer that relates your experience to the job requirements. Use concrete examples and be authentic."

def analyze_interview_performance(answers: List[str], job_requirements: str) -> Dict:
    """Analyze interview performance and provide feedback"""
    
    prompt = f"""
    Analyze these interview answers and provide constructive feedback.
    
    ANSWERS: {json.dumps(answers)}
    JOB REQUIREMENTS: {job_requirements[:500]}
    
    Provide feedback in this JSON format:
    {{
        "overall_score": <score out of 100>,
        "strengths": ["strength1", "strength2"],
        "areas_for_improvement": ["area1", "area2"],
        "specific_feedback": "detailed feedback text",
        "recommendations": ["recommendation1", "recommendation2"]
    }}
    
    Focus on practical, actionable feedback.
    """
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except:
        # Fallback feedback
        return {
            "overall_score": 75,
            "strengths": ["Good preparation", "Relevant examples"],
            "areas_for_improvement": ["Could be more specific", "Add more quantifiable results"],
            "specific_feedback": "Your answers show good preparation, but could benefit from more specific examples and quantifiable results.",
            "recommendations": ["Use the STAR method for behavioral questions", "Include metrics and specific outcomes"]
        }

