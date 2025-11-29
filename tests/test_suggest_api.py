from datetime import date, timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from infrastructure.api.state import set_last_analyzed_payload


class SuggestAPITests(APITestCase):
    def tearDown(self):
        set_last_analyzed_payload(None)

    def _analyze(self):
        payload = {
            "tasks": [
                {
                    "id": "today",
                    "title": "Due Today",
                    "due_date": date.today().isoformat(),
                    "estimated_hours": 2,
                    "importance": 7,
                    "dependencies": [],
                },
                {
                    "id": "tomorrow",
                    "title": "Due Tomorrow",
                    "due_date": (date.today() + timedelta(days=1)).isoformat(),
                    "estimated_hours": 5,
                    "importance": 5,
                    "dependencies": [],
                },
            ]
        }
        return self.client.post("/api/tasks/analyze/", data=payload, format="json")

    def test_suggest_uses_cached_payload_when_available(self):
        analyze_response = self._analyze()
        self.assertEqual(analyze_response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/tasks/suggest/?top_n=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "today")

    def test_suggest_returns_empty_results_without_payload(self):
        set_last_analyzed_payload(None)
        response = self.client.get("/api/tasks/suggest/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(response.data.get("message"), "no_tasks_provided")

    def test_suggest_post_seeds_cache(self):
        response = self.client.post(
            "/api/tasks/suggest/",
            data={"tasks": [{"id": "seed", "title": "Seed", "due_date": date.today().isoformat()}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_get = self.client.get("/api/tasks/suggest/")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["results"][0]["id"], "seed")
