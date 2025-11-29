# task_analyzer/urls.py

from django.urls import path, include # pyright: ignore[reportMissingModuleSource]
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie

# ensure CSRF cookie so frontend fetches can include the token
frontend_view = ensure_csrf_cookie(TemplateView.as_view(template_name="index.html"))

urlpatterns = [
    path("", frontend_view, name="frontend"),
    path("api/tasks/", include("infrastructure.api.urls")),
]
