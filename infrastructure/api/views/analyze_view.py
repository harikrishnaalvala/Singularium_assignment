"""
HTTP view adapter for analyze endpoint.

Purpose:
- receive POST requests with tasks payload
- validate HTTP payload using serializers
- call application service to perform analysis
- return structured JSON response with priority list, blocked tasks, warnings, and config used

Inputs:
- HTTP request with JSON body matching AnalyzePayloadSerializer

Outputs:
- HTTP JSON response with analysis results or validation/error details
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from infrastructure.api.serializers.task_serializer import AnalyzePayloadSerializer
from application.services.analyze_tasks_service import analyze_tasks_service
from infrastructure.api.state import set_last_analyzed_payload


class AnalyzeView(APIView):
    """
    POST handler for task analysis.

    Request body:
    {
      "tasks": [ { task objects } ],
      "config": { optional config overrides }
    }

    Response:
    {
      "priority_list": [...],
      "blocked_tasks": [...],
      "needs_attention": [...],
      "warnings": [...],
      "config_used": { ... }
    }
    """

    def post(self, request):
        serializer = AnalyzePayloadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "invalid_payload", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated = serializer.validated_data
        tasks_payload = validated.get("tasks", [])
        config_overrides = validated.get("config", {})

        try:
            result = analyze_tasks_service(tasks_payload, config_overrides)
            set_last_analyzed_payload(tasks_payload)
            return Response({"results": result}, status=status.HTTP_200_OK)
        except Exception as exc:
            # Log the exception in production; return minimal error info here
            return Response(
                {"error": "analysis_failed", "details": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
