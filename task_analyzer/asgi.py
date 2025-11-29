"""
ASGI config for Smart Task Analyzer.

Used for async servers (Daphne, Uvicorn) or WebSocket support.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_analyzer.settings")

application = get_asgi_application()
