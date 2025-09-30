import json
import google.generativeai as genai
from django.conf import settings
from typing import Dict, List
from fpdf import FPDF

# Configure Gemini AI
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Template definitions - SIMPLIFIED TO FOCUS ON SECTION ORDER ONLY
TEMPLATES = {
    "traditional": {
        "description": "Traditional linear layout",
        "section_order": ["header", "summary", "skills", "experience", "education", "certifications"]
    },
    "modern": {
        "description": "Modern experience-focused layout",
        "section_order": ["header", "summary", "experience", "skills", "education", "certifications"]
    },
    "hybrid": {
        "description": "Skills-first hybrid layout",
        "section_order": ["header", "skills", "summary", "experience", "education", "certifications"]
    }
}

def analyze_resume_gaps(resume_text: str, job_description: str) -> dict:
    """Analyze gaps between resume and job description"""
    prompt = f"""
    Analyze the resume against the job description and identify gaps. Return ONLY a JSON object with this exact structure:
    
    {{
        "must_have_skills_missing": ["skill1", "skill2"],
        "good_to_have_skills_missing": ["skill1", "skill2"],
        "matching_skills_to_emphasize": ["skill1", "skill2"],
        "quantifiable_achievements": ["achievement1", "achievement2"],
        "keywords_to_incorporate": ["keyword1", "keyword2"]
    }}
    
    Resume:
    {resume_text[:2000]}
    
    Job Description:
    {job_description[:1500]}
    
    Return only the JSON object, no other text.
    """
    
    try:
        response = model.generate_content(prompt)
        import json
        return json.loads(response.text.strip())
    except Exception as e:
        return {
            "must_have_skills_missing": [],
            "good_to_have_skills_missing": [],
            "matching_skills_to_emphasize": [],
            "quantifiable_achievements": [],
            "keywords_to_incorporate": []
        }

def generate_tailored_resume(resume_text: str, job_description: str, template_name: str, custom_skills: str = '', remove_sections: list = None, additional_notes: str = '') -> str:
    """Generate a tailored resume using AI with specific template formatting"""
    if remove_sections is None:
        remove_sections = []
    
    # Validate template name
    if template_name not in TEMPLATES:
        raise ValueError(f"Invalid template name: {template_name}. Available templates: {list(TEMPLATES.keys())}")
    
    template = TEMPLATES[template_name]
    print(f"\n=== FORCED TEMPLATE GENERATION ===")
    print(f"SELECTED TEMPLATE: {template_name.upper()}")
    print(f"EXPECTED ORDER: {' -> '.join(template['section_order'])}")
    print(f"=== SENDING TO AI ===")
    
    try:
        # First, perform gap analysis
        gap_analysis = analyze_resume_gaps(resume_text, job_description)
        
        # NUCLEAR OPTION: COMPLETELY DIFFERENT PROMPTS PER TEMPLATE
        if template_name == 'traditional':
            prompt = f"""
You are creating a TRADITIONAL resume. This means SUMMARY comes before SKILLS.

STRICT ORDER: HEADER -> SUMMARY -> SKILLS -> EXPERIENCE -> EDUCATION -> CERTIFICATIONS

CRITICAL INSTRUCTIONS:
- ONLY use the existing work experience from the original resume
- DO NOT create fake experience based on the job description
- DO NOT add the target company as work experience
- TAILOR existing experience to match job requirements
- The job description is what we're APPLYING FOR, not what we've done

{f"CUSTOM SKILLS TO EMPHASIZE: {custom_skills}" if custom_skills else ""}
{f"SECTIONS TO REMOVE: {', '.join(remove_sections)}" if remove_sections else ""}
{f"ADDITIONAL CUSTOMIZATION: {additional_notes}" if additional_notes else ""}

Original Resume: {resume_text}
Job Description (TARGET ROLE - DO NOT ADD AS EXPERIENCE): {job_description}

Create a resume with this EXACT structure:
1. HEADER (name, contact info)
2. SUMMARY (professional summary paragraph)
3. SKILLS (technical and soft skills)
4. EXPERIENCE (ONLY existing work experience from original resume - tailor descriptions to match job requirements)
5. EDUCATION (education history)
6. CERTIFICATIONS (certifications and licenses)

This is TRADITIONAL format - SUMMARY BEFORE SKILLS.
"""
        elif template_name == 'modern':
            prompt = f"""
You are creating a MODERN resume. This means EXPERIENCE comes before SKILLS.

STRICT ORDER: HEADER -> SUMMARY -> EXPERIENCE -> SKILLS -> EDUCATION -> CERTIFICATIONS

CRITICAL INSTRUCTIONS:
- ONLY use the existing work experience from the original resume
- DO NOT create fake experience based on the job description
- DO NOT add the target company as work experience
- TAILOR existing experience to match job requirements
- The job description is what we're APPLYING FOR, not what we've done

{f"CUSTOM SKILLS TO EMPHASIZE: {custom_skills}" if custom_skills else ""}
{f"SECTIONS TO REMOVE: {', '.join(remove_sections)}" if remove_sections else ""}
{f"ADDITIONAL CUSTOMIZATION: {additional_notes}" if additional_notes else ""}

Original Resume: {resume_text}
Job Description (TARGET ROLE - DO NOT ADD AS EXPERIENCE): {job_description}

Create a resume with this EXACT structure:
1. HEADER (name, contact info)
2. SUMMARY (professional summary paragraph)
3. EXPERIENCE (ONLY existing work experience from original resume - tailor descriptions to match job requirements)
4. SKILLS (technical and soft skills after experience)
5. EDUCATION (education history)
6. CERTIFICATIONS (certifications and licenses)

This is MODERN format - EXPERIENCE BEFORE SKILLS.
"""
        elif template_name == 'hybrid':
            prompt = f"""
You are creating a HYBRID resume. This means SKILLS comes first after header.

STRICT ORDER: HEADER -> SKILLS -> SUMMARY -> EXPERIENCE -> EDUCATION -> CERTIFICATIONS

CRITICAL INSTRUCTIONS:
- ONLY use the existing work experience from the original resume
- DO NOT create fake experience based on the job description
- DO NOT add the target company as work experience
- TAILOR existing experience to match job requirements
- The job description is what we're APPLYING FOR, not what we've done

{f"CUSTOM SKILLS TO EMPHASIZE: {custom_skills}" if custom_skills else ""}
{f"SECTIONS TO REMOVE: {', '.join(remove_sections)}" if remove_sections else ""}
{f"ADDITIONAL CUSTOMIZATION: {additional_notes}" if additional_notes else ""}

Original Resume: {resume_text}
Job Description (TARGET ROLE - DO NOT ADD AS EXPERIENCE): {job_description}

Create a resume with this EXACT structure:
1. HEADER (name, contact info)
2. SKILLS (technical and soft skills first)
3. SUMMARY (professional summary paragraph)
4. EXPERIENCE (ONLY existing work experience from original resume - tailor descriptions to match job requirements)
5. EDUCATION (education history)
6. CERTIFICATIONS (certifications and licenses)

This is HYBRID format - SKILLS FIRST after header.
"""
        else:
            prompt = f"Create a resume from: {resume_text}"
        
        response = model.generate_content(prompt)
        tailored_content = response.text
        print(f"\n=== AI RESPONSE ANALYSIS ===")
        print(f"TEMPLATE SENT: {template_name.upper()}")
        print(f"CONTENT PREVIEW: {tailored_content[:300]}...")
        
        # Check if AI actually followed the section order
        sections_found = []
        content_lower = tailored_content.lower()
        for section in ['skills', 'summary', 'experience', 'education']:
            if section in content_lower:
                pos = content_lower.find(section)
                sections_found.append((section, pos))
        
        sections_found.sort(key=lambda x: x[1])  # Sort by position
        actual_order = [s[0] for s in sections_found]
        print(f"AI GENERATED ORDER: {' -> '.join(actual_order)}")
        expected_order = template['section_order'][1:]  # Skip header
        print(f"EXPECTED ORDER: {' -> '.join(expected_order)}")
        
        # Check if AI followed the order correctly
        if actual_order != expected_order[:len(actual_order)]:
            print(f"\n*** TEMPLATE MISMATCH DETECTED ***")
            print(f"AI IGNORED {template_name.upper()} INSTRUCTIONS!")
            print(f"This is why preview shows {template_name} but content is wrong")
        else:
            print(f"\n*** SUCCESS: AI FOLLOWED {template_name.upper()} TEMPLATE ***")
        print(f"=== END ANALYSIS ===\n")
        
        # Apply additional template-specific formatting
        formatted_content = format_resume_with_style(tailored_content, template_name)
        print(f"\n=== FINAL RESULT ===")
        print(f"TEMPLATE SAVED TO DB: {template_name.upper()}")
        print(f"FINAL CONTENT PREVIEW: {formatted_content[:200]}...")
        print(f"=== GENERATION COMPLETE ===\n")
        return formatted_content
        
    except Exception as e:
        # Fallback to basic formatting if AI fails
        return f"Error generating tailored resume: {str(e)}\n\nOriginal resume:\n{resume_text}"

def apply_template_formatting(text: str, template_name: str) -> str:
    """Apply proper formatting based on template style"""
    return format_resume_with_style(text, template_name)

def format_resume_with_style(text: str, template_name: str) -> str:
    """Apply minimal formatting - just ensure clean structure"""
    
    if template_name not in TEMPLATES:
        raise ValueError(f"Invalid template name: {template_name}. Available templates: {list(TEMPLATES.keys())}")
    
    template = TEMPLATES[template_name]
    
    # Just clean up the text and ensure proper spacing
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # Skip empty lines but preserve structure
        if not stripped_line:
            formatted_lines.append('')
            continue
            
        # Ensure section headers are uppercase
        if (len(stripped_line) < 50 and 
            not stripped_line.startswith(('•', '▪', '→', '-', '*')) and 
            not any(char.isdigit() for char in stripped_line[:5]) and
            (stripped_line.isupper() or 
            stripped_line.lower() in ['skills', 'experience', 'education', 'summary', 'certifications', 'work experience', 'relevant skills'])):
            
            formatted_lines.append(stripped_line.upper())
        else:
            # Regular content line
            formatted_lines.append(line)
    
    final_text = '\n'.join(formatted_lines)
    return final_text

def clean_resume_content(content):
    """Clean resume content by removing AI response messages and formatting properly"""
    lines = content.split('\n')
    cleaned_lines = []
    skip_until_name = True
    
    for line in lines:
        stripped = line.strip()
        
        # Skip AI response messages and introductory text
        if any(phrase in stripped.lower() for phrase in [
            "okay, here's",
            "here's the resume",
            "here's a resume",
            "based on the provided information",
            "i've created",
            "here is the resume",
            "following the requested format",
            "formatted in the",
            "adhering to the specified",
            "i have used the description",
            "don't you think this is",
            "i think previously it was"
        ]):
            continue
        
        # Skip until we find the actual name (first substantial content)
        if skip_until_name:
            if stripped and not any(skip_word in stripped.lower() for skip_word in [
                "okay", "here's", "based on", "formatted", "adhering", "style you requested"
            ]):
                # Check if this looks like a name (short line, likely contains letters)
                if len(stripped) < 100 and any(c.isalpha() for c in stripped):
                    skip_until_name = False
                    cleaned_lines.append(line)
            continue
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def save_resume_as_pdf(resume_content, filename):
    """Save resume content as PDF with proper formatting"""
    import tempfile
    import os
    
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Process text line by line with proper formatting
        lines = resume_content.split('\n')
        for line in lines:
            if line.strip():
                clean_line = line.strip()
                
                # Clean special characters that might cause issues
                clean_line = clean_line.replace("'", "'").replace('–', '-').replace('—', '-')
                clean_line = clean_line.replace('▪', '• ').replace('→', '• ')
                clean_line = clean_line.replace('**', '').replace('__', '')
                
                # Convert to latin-1 encoding to avoid character issues
                try:
                    clean_line = clean_line.encode('latin-1', 'ignore').decode('latin-1')
                except:
                    # If encoding fails, use ASCII fallback
                    clean_line = clean_line.encode('ascii', 'ignore').decode('ascii')
                
                try:
                    # Check if it's a section header - more comprehensive detection
                    is_section_header = False
                    
                    # Check for standard section headers
                    section_keywords = [
                        'summary', 'skills', 'experience', 'education', 'certifications', 
                        'work experience', 'relevant skills', 'professional summary',
                        'certifications & activities', 'achievements', 'projects',
                        'technical skills', 'soft skills', 'career objective'
                    ]
                    
                    # Check if line is a section header
                    if (clean_line.isupper() and len(clean_line) < 80) or \
                       (len(clean_line) < 80 and clean_line.lower().strip() in section_keywords) or \
                       (clean_line.startswith('**') and clean_line.endswith('**') and len(clean_line) < 80):
                        is_section_header = True
                    
                    if is_section_header:
                        # Remove markdown formatting if present
                        header_text = clean_line.replace('**', '').strip()
                        pdf.set_font("Arial", 'B', 14)  # Bold and larger headers
                        pdf.multi_cell(0, 8, header_text.upper())  # Force uppercase
                        pdf.ln(3)
                        pdf.set_font("Arial", size=10)  # Reset to normal
                    
                    # Check for section separators and draw actual lines
                    elif any(sep in clean_line for sep in ['===', '---', '~~~']):
                        pdf.ln(2)
                        pdf.set_draw_color(0, 0, 0)  # Black line
                        pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Draw line across page
                        pdf.ln(4)
                    
                    # Handle bullet points with actual bullets
                    elif clean_line.startswith('* ') or clean_line.startswith('• ') or clean_line.strip().startswith('*'):
                        # Use a simple dash instead of bullet character for better compatibility
                        if clean_line.startswith('* '):
                            clean_line = '- ' + clean_line[2:]
                        elif clean_line.strip().startswith('*'):
                            # Handle cases where * is not at the beginning due to indentation
                            clean_line = '- ' + clean_line.strip()[1:].strip()
                        elif clean_line.startswith('• '):
                            clean_line = '- ' + clean_line[2:]
                        
                        # Add some indentation for bullet points
                        pdf.set_x(15)  # Indent bullet points
                        pdf.multi_cell(0, 6, clean_line)
                        pdf.ln(1)
                    
                    # Regular text
                    else:
                        # Check if this is a very long line that needs better formatting
                        if len(clean_line) > 100 and any(keyword in clean_line.lower() for keyword in ['competitions:', 'social contributions:', 'extra curriculum:', 'projects/research:']):
                            # Split long certification/activity lines into better formatted sections
                            if ':' in clean_line:
                                parts = clean_line.split(':', 1)
                                # Make the category bold
                                pdf.set_font("Arial", 'B', 10)
                                pdf.multi_cell(0, 6, parts[0] + ':')
                                pdf.set_font("Arial", size=10)
                                
                                # Format the items with better spacing
                                if len(parts) > 1:
                                    items = parts[1].split(',')
                                    for i, item in enumerate(items):
                                        item = item.strip()
                                        if item:
                                            pdf.multi_cell(0, 6, '  - ' + item)
                                            pdf.ln(1)
                            else:
                                pdf.multi_cell(0, 6, clean_line)
                                pdf.ln(1)
                        else:
                            pdf.multi_cell(0, 6, clean_line)
                            pdf.ln(1)
                        
                except UnicodeEncodeError:
                    # If there's still an encoding issue, write a placeholder
                    pdf.multi_cell(0, 6, "[Content with special characters]")
                    pdf.ln(1)
                except Exception as e:
                    # Last resort: try to extract only ASCII characters
                    try:
                        simple_line = ''.join(c for c in clean_line if ord(c) < 128)
                        if simple_line.strip():
                            pdf.multi_cell(0, 6, simple_line)
                            pdf.ln(1)
                    except:
                        continue
            else:
                pdf.ln(3)
        
        # Create a temporary file and save PDF to it, then read back
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            temp_filename = tmp_file.name
        
        # Save PDF to temporary file
        pdf.output(temp_filename)
        
        # Read the file back as bytes
        with open(temp_filename, 'rb') as f:
            pdf_bytes = f.read()
        
        # Clean up temporary file
        try:
            os.unlink(temp_filename)
        except:
            pass
            
        return pdf_bytes
            
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")
