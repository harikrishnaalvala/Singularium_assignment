"""
URL routing for tasks API exposed by infrastructure layer.

Routes:
- POST /api/tasks/analyze/ -> AnalyzeView.post
- GET  /api/tasks/suggest/  -> SuggestView.get
- POST /api/tasks/suggest/ -> SuggestView.post (cache update)
"""

from django.urls import path, include # pyright: ignore[reportMissingModuleSource]
from infrastructure.api.views.analyze_view import AnalyzeView
from infrastructure.api.views.suggest_view import SuggestView

urlpatterns = [
    path("analyze/", AnalyzeView.as_view(), name="api-tasks-analyze"),
    path("suggest/", SuggestView.as_view(), name="api-tasks-suggest"),
]
