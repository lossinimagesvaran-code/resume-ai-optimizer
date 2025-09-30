"""
WSGI config for resume_optimizer project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_optimizer.settings')

application = get_wsgi_application()

