from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from infrastructure.api.state import set_last_analyzed_payload


class AnalyzeAPITests(APITestCase):
    def tearDown(self):
        set_last_analyzed_payload(None)

    def test_analyze_returns_sorted_priority_list(self):
        payload = {
            "tasks": [
                {
                    "id": "urgent",
                    "title": "Urgent Task",
                    "due_date": date.today().isoformat(),
                    "estimated_hours": 1,
                    "importance": 6,
                    "dependencies": [],
                },
                {
                    "id": "later",
                    "title": "Later Task",
                    "due_date": (date.today() + timedelta(days=7)).isoformat(),
                    "estimated_hours": 2,
                    "importance": 9,
                    "dependencies": [],
                },
            ]
        }

        response = self.client.post("/api/tasks/analyze/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data["results"]
        priority_list = results["priority_list"]
        scores = [entry["score"] for entry in priority_list]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(results["blocked_tasks"], [])
        self.assertEqual(results["warnings"], [])

    def test_analyze_detects_cycles_and_reports_blocked_tasks(self):
        payload = {
            "tasks": [
                {
                    "id": "A",
                    "title": "Task A",
                    "due_date": (date.today() + timedelta(days=1)).isoformat(),
                    "estimated_hours": 2,
                    "importance": 5,
                    "dependencies": ["B"],
                },
                {
                    "id": "B",
                    "title": "Task B",
                    "due_date": (date.today() + timedelta(days=2)).isoformat(),
                    "estimated_hours": 3,
                    "importance": 5,
                    "dependencies": ["A"],
                },
            ]
        }

        response = self.client.post("/api/tasks/analyze/", data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        blocked_ids = {task["id"] for task in response.data["results"]["blocked_tasks"]}
        self.assertSetEqual(blocked_ids, {"A", "B"})

    def test_analyze_rejects_invalid_payload(self):
        response = self.client.post("/api/tasks/analyze/", data={"tasks": {}}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
