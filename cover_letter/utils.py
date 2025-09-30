import json
from datetime import date
import google.generativeai as genai
from django.conf import settings
from typing import Dict, List
from fpdf import FPDF

# Configure Gemini AI
genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_cover_letter_with_ai(
    personal_info: Dict,
    company_info: Dict,
    resume_text: str,
    job_description: str,
    writing_style: str = "professional",
    focus_areas: List[str] = None,
    additional_notes: str = ""
) -> str:
    """Generate a professional cover letter using AI"""
    
    if focus_areas is None:
        focus_areas = []
    
    current_date = date.today().strftime("%B %d, %Y")
    
    # Build the prompt for AI
    prompt = f"""
    Write a professional cover letter using this exact format and information:
    
    PERSONAL INFORMATION:
    - Name: {personal_info['full_name']}
    - Address: {personal_info.get('address', personal_info.get('full_address', 'Not provided'))}
    - Phone: {personal_info.get('phone', personal_info.get('phone_number', 'Not provided'))}
    - Email: {personal_info['email']}
    
    COMPANY INFORMATION:
    - Company: {company_info['name']}
    - Company Address: {company_info.get('address', company_info.get('company_address', 'Not provided'))}
    - Job Title: {company_info['job_title']}
    - Date: {current_date}
    
    WRITING STYLE: {writing_style}
    FOCUS AREAS: {', '.join(focus_areas) if focus_areas else 'All areas'}
    ADDITIONAL NOTES: {additional_notes if additional_notes else 'None'}
    
    IMPORTANT: Replace ALL placeholders with actual information:
    - Use "{personal_info['full_name']}" instead of "[Your Name]"
    - Use "{personal_info.get('address', personal_info.get('full_address', ''))}" instead of "[Your Address]"
    - Use "{personal_info.get('phone', personal_info.get('phone_number', ''))}" instead of "[Your Phone Number]"
    - Use "{personal_info['email']}" instead of "[Your Email Address]"
    - Use "{company_info['name']}" instead of company placeholders
    - Use "{company_info.get('address', company_info.get('company_address', ''))}" instead of "[Company Address]"
    
    COVER LETTER STRUCTURE:
    1. Header with actual personal and company information (NO PLACEHOLDERS)
    2. Opening paragraph: Reason for writing and position interest
    3. Body paragraphs: Relevant experience, skills, and achievements
    4. Closing paragraph: Request for interview and contact details
    
    REQUIREMENTS:
    - DO NOT use any placeholders like [Your Name], [Your Address], etc.
    - Use actual names, addresses, phone numbers, and email addresses provided
    - Use the specified writing style
    - Focus on the selected focus areas
    - Incorporate relevant information from the resume
    - Address the job description requirements
    - Keep it professional and engaging
    - Use proper business letter format
    
    RESUME CONTENT (for reference):
    {resume_text[:1000]}
    
    JOB DESCRIPTION (for reference):
    {job_description[:1000]}
    
    Write a complete, professional cover letter with NO PLACEHOLDERS - use all actual information provided.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Fallback to basic cover letter if AI fails
        return generate_fallback_cover_letter(
            personal_info, company_info, current_date, writing_style
        )

def generate_fallback_cover_letter(
    personal_info: Dict,
    company_info: Dict,
    current_date: str,
    writing_style: str
) -> str:
    """Generate a basic cover letter if AI fails"""
    
    # Basic cover letter template
    cover_letter = f"""
{personal_info['full_name']}
{personal_info['address']}
{personal_info.get('phone', '')}
{personal_info['email']}

{current_date}

{company_info['name']}
{company_info.get('address', '')}

Subject: Application for {company_info['job_title']} Position

Dear Hiring Manager,

I am writing to express my strong interest in the {company_info['job_title']} position at {company_info['name']}. With my background and experience, I am confident that I can make valuable contributions to your team.

I have reviewed the job requirements and believe my skills and experience align well with what you are seeking. I am particularly excited about the opportunity to work with {company_info['name']} and contribute to its continued success.

I would welcome the opportunity to discuss how my background, skills, and enthusiasm can benefit {company_info['name']}. I am available for an interview at your convenience and can be reached at {personal_info['email']} or {personal_info.get('phone', 'my email')}.

Thank you for considering my application. I look forward to hearing from you.

Sincerely,
{personal_info['full_name']}
"""
    
    return cover_letter.strip()

def save_cover_letter_as_pdf(cover_letter_content, filename):
    """Save cover letter content as PDF with proper formatting - Fixed horizontal space issue"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Set margins to ensure proper spacing
        pdf.set_margins(left=20, top=20, right=20)
        
        # Set font properly
        pdf.set_font("Arial", size=12)
        
        # Clean the text for PDF - replace problematic characters
        text = cover_letter_content.replace("'", "'").replace('–', '-').replace('—', '-')
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        # Replace special bullets with standard ones for better compatibility
        bullet_mapping = {
            '•': '* ',
            '▪': '* ',
            '→': '* ',
            '**': '',  # Remove markdown bold
            '*': '',   # Remove remaining markdown
        }
        
        for old, new in bullet_mapping.items():
            text = text.replace(old, new)
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Encode to latin1 to avoid character issues
                try:
                    clean_line = line.encode('latin1', 'ignore').decode('latin1')
                except:
                    clean_line = line
                
                # Handle headers (uppercase lines or lines that look like headers)
                if (clean_line.isupper() and len(clean_line) < 50) or any(header in clean_line.upper() for header in ['DEAR', 'SINCERELY', 'SUBJECT:']):
                    pdf.set_font("Arial", 'B', 14)
                    pdf.multi_cell(0, 10, clean_line)  # Use multi_cell instead of cell
                    pdf.ln(5)
                    pdf.set_font("Arial", size=12)
                
                # Handle section separators
                elif any(sep in clean_line for sep in ['---', '===', '~~~']):
                    pdf.ln(3)
                    pdf.set_draw_color(100, 100, 100)
                    pdf.line(20, pdf.get_y(), 190, pdf.get_y())  # Adjust line coordinates
                    pdf.ln(3)
                
                # Handle regular text
                else:
                    pdf.set_font("Arial", size=12)
                    
                    # Handle bullet points or indented text
                    if clean_line.startswith('* ') or clean_line.startswith('- '):
                        # Add bullet point manually
                        pdf.cell(10, 6, '•', ln=0)  # Add bullet
                        # Calculate remaining width for text
                        remaining_width = pdf.w - pdf.l_margin - pdf.r_margin - 10
                        pdf.multi_cell(remaining_width, 6, clean_line[2:].strip())
                    else:
                        # Regular paragraph text
                        pdf.multi_cell(0, 6, clean_line)
                    
                    pdf.ln(2)
            else:
                # Empty line - add some space
                pdf.ln(4)
        
        # Save to file and return bytes
        pdf.output(filename)
        with open(filename, 'rb') as f:
            return f.read()
            
    except Exception as e:
        # Enhanced fallback with better error handling
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(left=20, top=20, right=20)
            pdf.set_font("Arial", size=12)
            
            # Simple line-by-line processing for fallback
            lines = cover_letter_content.split('\n')
            for line in lines:
                if line.strip():
                    # Clean line for latin1 encoding
                    clean_line = line.strip()
                    try:
                        clean_line = clean_line.encode('latin1', 'ignore').decode('latin1')
                    except:
                        clean_line = ''.join(c for c in clean_line if ord(c) < 256)
                    
                    # Replace problematic characters
                    clean_line = clean_line.replace('•', '* ').replace('▪', '* ').replace('→', '* ')
                    
                    if clean_line:
                        pdf.multi_cell(0, 8, clean_line)
                        pdf.ln(2)
                else:
                    pdf.ln(4)
            
            pdf.output(filename)
            with open(filename, 'rb') as f:
                return f.read()
                
        except Exception as fallback_error:
            # Last resort: create a simple PDF with error message
            pdf = FPDF()
            pdf.add_page()
            pdf.set_margins(left=20, top=20, right=20)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, "Error generating PDF. Please try downloading as text format.")
            pdf.multi_cell(0, 10, f"Original content length: {len(cover_letter_content)} characters")
            
            pdf.output(filename)
            with open(filename, 'rb') as f:
                return f.read()

def format_cover_letter_content(content: str, font_size: str = "medium", line_spacing: str = "1.5") -> str:
    """Format cover letter content with specified styling"""
    
    # Convert font size to points
    font_sizes = {
        "small": 10,
        "medium": 12,
        "large": 14
    }
    
    # Convert line spacing to multiplier
    spacing_multipliers = {
        "single": 1.0,
        "1.5": 1.5,
        "double": 2.0
    }
    
    # Apply formatting (this would be used in the PDF generation)
    # For now, return the content as-is
    return content

