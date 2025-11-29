"""
WSGI config for Smart Task Analyzer.

Used for deployments using WSGI-based servers (Gunicorn, uWSGI).
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_analyzer.settings")

application = get_wsgi_application()
