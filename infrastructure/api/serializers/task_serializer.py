"""
HTTP serializers for the Tasks API.

Purpose:
- Validate the incoming HTTP JSON shape
- Provide helpful error messages to clients
- Keep strict but minimal validation; heavy normalization is delegated
  to the application layer

Inputs:
- JSON request body for analyze endpoint which must contain a key "tasks"
  mapping to a list of task objects. Each task object may contain fields:
    id, title, due_date, estimated_hours, importance, dependencies

Outputs:
- validated data that application services can consume directly
"""

from rest_framework import serializers


class SingleTaskSerializer(serializers.Serializer):
    """
    Serializer for a single task object.

    Fields:
      - id: optional string
      - title: optional string
      - due_date: optional string (ISO or other formats)
      - estimated_hours: optional float
      - importance: optional integer
      - dependencies: optional list of strings
    """
    id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    title = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(required=False, allow_null=True)
    dependencies = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True
    )


class AnalyzePayloadSerializer(serializers.Serializer):
    """
    Serializer for analyze request payload.

    Expected top level shape:
    {
      "tasks": [ { ... }, { ... } ],
      "config": { optional overrides }
    }
    """
    tasks = serializers.ListSerializer(child=SingleTaskSerializer(), required=True)
    config = serializers.DictField(required=False)
