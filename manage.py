#!/usr/bin/env python3
"""
Django management utility for the Smart Task Analyzer project.

Purpose:
- Acts as the command-line entry point for running the development server,
  applying migrations, creating superusers, executing tests, etc.
- Loads environment configuration and the project's Django settings.

Usage Examples:
    python manage.py runserver
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py test
"""

import os
import sys


def main():
    """
    Main execution entry point.

    Sets the default settings module and hands control to Django's CLI
    management framework. Any startup-level environment initialization
    (e.g., dotenv loading) can also be done here.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_analyzer.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Ensure it is installed and available "
            "on your PYTHONPATH environment variable. You may need to activate "
            "your virtual environment."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
