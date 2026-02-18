# Resume AI Optimizer
A comprehensive, AI-powered career development platform built with Django that revolutionizes job search preparation. This system combines advanced AI technology with professional career tools to help job seekers create ATS-optimized resumes, generate personalized cover letters, master interview preparation, and even get style recommendations for professional appearance.

## ✨ Core Features

###  **Intelligent Resume Analysis & ATS Optimization**
- **Advanced PDF Text Extraction** using PyMuPDF with error handling
- **AI-Powered Gap Analysis** comparing resume against job descriptions
- **ATS Compatibility Scoring** with detailed keyword matching
- **Actionable Improvement Recommendations** with specific suggestions
- **Match Score Calculation** with percentage-based feedback
- **Session-Based Data Persistence** for seamless user experience

###  **AI-Powered Resume Tailoring System**
- **3 Professional Templates**: Traditional, Modern, and Hybrid layouts
- **Intelligent Content Rewriting** using Google Gemini 2.0 Flash
- **Dynamic Keyword Integration** from job descriptions
- **Customizable Focus Areas** and writing tones
- **Multi-Format Export**: TXT and PDF with professional formatting
- **Template-Specific Formatting** with visual consistency

###  **Smart Cover Letter Generator**
- **AI-Driven Personalization** based on resume and job requirements
- **Company-Specific Customization** with role-targeted content
- **Multiple Writing Styles** and professional focus areas
- **Professional Template System** with consistent formatting
- **Export Capabilities** with PDF generation

###  **Progressive Interview Preparation System**
- **3-Level Gamified Learning**: Essential → Advanced → Expert
- **AI-Powered Interview Coaching** with personalized tips
- **Interactive Chat Interface** with context-aware responses
- **Progress Tracking** with completion percentages
- **Tip Management System** with database persistence
- **PDF Export** for comprehensive preparation guides

###  **AI Style & Fashion Advisory (Bonus Feature)**
- **Computer Vision Skin Tone Analysis** using OpenCV
- **AI-Powered Style Recommendations** with 10,000+ fashion products
- **Professional Color Palette Suggestions** based on skin analysis
- **Fashion Dataset Integration** with CSV-based product database
- **Image Processing** for personalized styling advice

##  Complete Technology Stack

### ** Backend Framework**
- **Django 4.2.7** - Main web framework with MVC architecture
- **Python 3.8+** - Core programming language
- **Django ORM** - Database abstraction layer
- **Django Sessions** - User session management
- **Django Messages** - User feedback system

### ** AI & LLM Integration**
- **Google Gemini 2.0 Flash** - Primary AI engine for content generation
- **google-generativeai 0.3.2** - Official Google AI SDK
- **Custom Prompt Engineering** - Structured prompts for consistent output
- **Context-Aware AI Responses** - Resume and job description context integration
- **No LangChain** - Direct API integration for optimal performance

### ** Database & Data Management**
- **SQLite** - Development database (production-ready)
- **PostgreSQL/MySQL Support** - Configurable for production
- **Django Migrations** - Database schema management
- **Model Relationships** - Foreign keys and data integrity
- **Session Storage** - Temporary data persistence

### ** NLP & File Processing**
- **PyMuPDF (fitz) 1.23.8** - PDF text extraction and processing
- **FPDF2 2.7.6** - PDF generation and formatting
- **Pillow 10.1.0** - Image processing for skin tone analysis
- **OpenCV Integration** - Computer vision for style recommendations
- **Text Processing** - Custom content cleaning and formatting

### ** Frontend & UI Framework**
- **Bootstrap 5** - Responsive CSS framework
- **HTML5/CSS3** - Modern web standards
- **JavaScript (Vanilla)** - Interactive functionality
- **Django Crispy Forms** - Enhanced form rendering
- **crispy-bootstrap5 0.7** - Bootstrap 5 integration

### ** Additional Libraries & Tools**
- **python-dotenv 1.0.0** - Environment variable management
- **django-environ 0.11.2** - Settings configuration
- **whitenoise 6.6.0** - Static file serving
- **gunicorn 21.2.0** - Production WSGI server
- **django-allauth 0.57.0** - Authentication system (optional)

### ** Operating System Compatibility**
- **Windows** - Primary development and testing environment
- **Linux** - Production deployment ready
- **macOS** - Cross-platform compatibility
- **Docker Support** - Containerization ready

##  System Requirements

- **Python 3.8+** (Tested on Python 3.11)
- **Google Gemini API Key** (Required for AI features)
- **Virtual Environment** (Highly recommended)
- **10MB+ Storage** for media files and database
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

##  Quick Start Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ResumeOptimiser
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your configuration
```

**Required Environment Variables:**
```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini AI API (REQUIRED)
GOOGLE_API_KEY=your-google-gemini-api-key-here

# Database (SQLite by default)
DATABASE_URL=sqlite:///db.sqlite3

# Static and Media Files
STATIC_URL=/static/
MEDIA_URL=/media/
```

### 5. Database Setup
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create admin user (optional)
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

 **Access the application at:** `http://127.0.0.1:8000/`

##  Advanced Configuration

###  Google Gemini AI API Setup
1. **Visit** [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Create** a new API key
3. **Add** the key to your `.env` file as `GOOGLE_API_KEY`
4. **Test** the connection by running the application

##  Complete User Guide

###  **Step 1: Resume Analysis**
1. **Upload** your PDF resume (supports multiple formats)
2. **Paste** the target job description
3. **Click** "Analyze Resume" to get AI-powered insights
4. **Review** match score, keyword analysis, and improvement suggestions
5. **Use** the analysis data for subsequent features

###  **Step 2: Resume Tailoring**
1. **Select** from 3 professional templates:
   - **Traditional**: Linear layout with clear sections
   - **Modern**: Spaced-out design with creative elements
   - **Hybrid**: Skill-focused flexible structure
2. **Customize** focus areas and writing preferences
3. **Generate** ATS-optimized tailored resume
4. **Preview** and edit the generated content
5. **Download** in TXT or PDF format

###  **Step 3: Cover Letter Generation**
1. **Input** personal and company information
2. **Select** writing style and focus areas
3. **Generate** AI-personalized cover letter
4. **Review** and edit the generated content
5. **Export** as PDF for applications

###  **Step 4: Interview Preparation**
1. **Generate** Level 1 essential tips (5 tips)
2. **Complete** tips by checking them off
3. **Unlock** Level 2 advanced tips
4. **Progress** through Level 3 expert tips
5. **Use** AI chat coach for specific questions
6. **Download** comprehensive preparation guide

###  **Bonus: Style Advisory**
1. **Upload** a photo for skin tone analysis
2. **Get** AI-powered color palette recommendations
3. **Browse** curated fashion suggestions
4. **Apply** professional styling advice

##  Detailed Project Architecture

```
ResumeOptimiser/
├── 📁 resume_optimizer/          # Main Django Project
│   ├── settings.py              # Configuration & environment
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py                  # WSGI application
│   └── context_processors.py    # Global template context
├── 📁 core/                      # Core Application
│   ├── views.py                 # Home, dashboard, about pages
│   ├── urls.py                  # Core URL patterns
│   └── apps.py                  # App configuration
├── 📁 resume_analysis/           # Resume Analysis Engine
│   ├── models.py                # ResumeUpload, ResumeAnalysis
│   ├── views.py                 # Analysis workflow
│   ├── utils.py                 # AI analysis functions
│   └── forms.py                 # Upload forms
├── 📁 resume_tailoring/          # Resume Tailoring System
│   ├── models.py                # TailoredResume model
│   ├── views.py                 # Template selection & generation
│   ├── utils.py                 # AI content generation
│   └── forms.py                 # Customization forms
├── 📁 cover_letter/              # Cover Letter Generator
│   ├── models.py                # CoverLetter model
│   ├── views.py                 # Generation workflow
│   ├── utils.py                 # AI letter generation
│   └── forms.py                 # Letter forms
├── 📁 interview_prep/            # Interview Preparation
│   ├── models.py                # InterviewTip, InterviewChat, InterviewSession
│   ├── views.py                 # Progressive learning system
│   ├── utils.py                 # AI coaching functions
│   └── forms.py                 # Interview forms
├── 📁 clothing_advisor/          # Style Advisory System
│   ├── models.py                # SkinAnalysis, StyleRecommendation
│   ├── views.py                 # Style analysis workflow
│   ├── ai_agents.py             # AI styling agents
│   ├── skin_tone_detector.py    # Computer vision analysis
│   └── fashion_dataset.py       # Product database management
├── 📁 templates/                 # HTML Templates
│   ├── base.html                # Base template with navigation
│   ├── 📁 core/                 # Core app templates
│   ├── 📁 resume_analysis/      # Analysis templates
│   ├── 📁 resume_tailoring/     # Tailoring templates
│   ├── 📁 cover_letter/         # Cover letter templates
│   ├── 📁 interview_prep/       # Interview prep templates
│   └── 📁 clothing_advisor/     # Style advisor templates
├── 📁 static/                    # Static Assets
│   ├── 📁 css/                  # Custom stylesheets
│   └── 📁 js/                   # JavaScript functionality
├── 📁 media/                     # User Uploads
│   ├── 📁 resumes/              # PDF resume files
│   └── *.jpg                    # Skin analysis images
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env                       # Environment variables
├── 📄 env_example.txt            # Environment template
├── 📄 db.sqlite3                 # SQLite database
├── 📄 scraped_fashion_products.csv # Fashion dataset
└── 📄 manage.py                  # Django management
```

##  Support & Troubleshooting

### Common Issues
**API Key Errors:**
- Verify your Google Gemini API key is valid
- Check API quotas and billing
- Ensure proper environment variable setup

**PDF Upload Issues:**
- Check file size limits (10MB default)
- Verify PDF is not password-protected
- Ensure PDF contains extractable text

**Database Errors:**
- Run migrations: `python manage.py migrate`
- Check database permissions
- Verify database connection settings

