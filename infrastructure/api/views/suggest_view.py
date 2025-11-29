"""
HTTP view adapter for suggest endpoint.

Purpose:
- return top suggested tasks to work on today
- uses the same request shape for optional config overrides but only acts on cached
  or immediate payload provided by client

Inputs:
- GET request may include query param 'top_n' and optional JSON body with tasks
- If no body is provided, view will attempt to use last-analyzed tasks kept in-memory

Outputs:
- list of suggested tasks with short reasons and metadata
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from application.services.suggest_tasks_service import suggest_tasks_service
from infrastructure.api.state import get_last_analyzed_payload, set_last_analyzed_payload


class SuggestView(APIView):
    """
    GET handler to produce suggested tasks.

    Behavior:
    - If client provides JSON list of tasks in the request body, analyze those
      and return top suggestions
    - Otherwise, if analyze endpoint was called earlier during runtime, use the
      cached payload to compute suggestions
    - Accepts optional query parameter 'top_n' to control how many suggestions to
      return. Defaults to three.
    """

    parser_classes = [JSONParser]

    def get(self, request):
        try:
            # try to read JSON body if present
            body = request.data or {}
            tasks_payload = body.get("tasks") if isinstance(body, dict) else None

            if isinstance(tasks_payload, list):
              set_last_analyzed_payload(tasks_payload)
            else:
              tasks_payload = get_last_analyzed_payload()

            if not tasks_payload:
                return Response({"results": [], "message": "no_tasks_provided"}, status=status.HTTP_200_OK)

            # read top_n from query params; if missing fall back to default
            try:
                top_n = int(request.query_params.get("top_n") or 3)
            except Exception:
                top_n = 3

            suggestions = suggest_tasks_service(tasks_payload, top_n=top_n)
            return Response({"results": suggestions}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": "suggest_failed", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
      """Allow clients to seed the suggestion cache with an explicit task list."""

      if isinstance(request.data, dict) and isinstance(request.data.get("tasks"), list):
        set_last_analyzed_payload(request.data.get("tasks"))
        return Response({"message": "cached"}, status=status.HTTP_200_OK)

      return Response({"error": "invalid_payload"}, status=status.HTTP_400_BAD_REQUEST)
