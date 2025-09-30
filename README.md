# Resume AI Optimizer - Complete Career Assistant Platform

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

###  Database Configuration Options

**Development (Default - SQLite):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production (PostgreSQL):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'resume_optimizer_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Production (MySQL):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resume_optimizer_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

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

##  Customization & Extension Guide

###  Adding New Resume Templates
```python
# In resume_tailoring/utils.py
TEMPLATES = {
    'your_template': {
        'name': 'Your Template Name',
        'description': 'Template description',
        'section_order': ['header', 'summary', 'skills', 'experience'],
        'formatting': {
            'bullet_style': '• ',
            'section_separator': '\n' + '-' * 50 + '\n',
            'header_style': 'BOLD_CAPITALIZE'
        }
    }
}
```

###  Customizing AI Prompts
**Resume Analysis Prompts:**
```python
# In resume_analysis/utils.py
def analyze_resume_match(resume_text, job_description):
    prompt = f"""
    Your custom analysis prompt here...
    Resume: {resume_text}
    Job Description: {job_description}
    """
```

**Interview Coaching Prompts:**
```python
# In interview_prep/utils.py
def generate_interview_tips(resume_text, job_description, level):
    level_prompts = {
        1: "Your Level 1 prompt...",
        2: "Your Level 2 prompt...",
        3: "Your Level 3 prompt..."
    }
```

###  UI/UX Customization
**Custom Styling:**
```css
/* In static/css/style.css */
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    --accent-color: #your-color;
}
```

**JavaScript Enhancements:**
```javascript
// In static/js/main.js
// Add your custom functionality
function customFeature() {
    // Your code here
}
```

###  Adding New Features
1. **Create new Django app**: `python manage.py startapp your_feature`
2. **Add to INSTALLED_APPS** in settings.py
3. **Create models, views, templates**
4. **Add URL patterns**
5. **Update navigation** in base.html

##  Production Deployment Guide

###  Production Configuration
```env
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-secure-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address
GOOGLE_API_KEY=your-production-gemini-api-key

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Static Files
STATIC_ROOT=/var/www/static/
MEDIA_ROOT=/var/www/media/

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

###  Docker Deployment
**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "resume_optimizer.wsgi:application"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/resume_optimizer
    depends_on:
      - db
    volumes:
      - media_volume:/app/media
      - static_volume:/app/staticfiles

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=resume_optimizer
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  media_volume:
  static_volume:
```

###  Cloud Deployment Options

**Heroku Deployment:**
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set GOOGLE_API_KEY=your-api-key
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
```

**AWS EC2 Deployment:**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Setup application
git clone your-repo
cd ResumeOptimiser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure Nginx
sudo nano /etc/nginx/sites-available/resume_optimizer

# Start services
sudo systemctl start nginx
sudo systemctl enable nginx
gunicorn --bind 0.0.0.0:8000 resume_optimizer.wsgi:application
```

##  Testing & Quality Assurance

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test resume_analysis
python manage.py test resume_tailoring
python manage.py test interview_prep

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality
```bash
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Check code quality
flake8 .
```

##  Security Considerations

- **API Key Protection**: Never commit API keys to version control
- **Input Validation**: All user inputs are validated and sanitized
- **File Upload Security**: PDF files are scanned and validated
- **CSRF Protection**: Enabled for all forms
- **SQL Injection Prevention**: Using Django ORM exclusively
- **XSS Protection**: Template auto-escaping enabled

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


---

## 🎯 **Project Status: Production Ready**

**Built using Django and cutting-edge AI technology to revolutionize job search preparation and help career seekers succeed in today's competitive market.**

