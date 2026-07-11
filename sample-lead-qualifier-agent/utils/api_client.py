# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from collections.abc import Generator
from typing import Any

import requests


class RandstadApiClient:
    """
    Client sincrono per interagire con l'API dell'Agente Randstad.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000", token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def health_check(self) -> bool:
        """Verifica se il server è attivo tramite l'endpoint /health."""
        try:
            response = requests.get(f"{self.base_url}/health", headers=self.headers, timeout=5)
            return response.status_code == 200 and response.json().get("status") == "ok"
        except Exception:
            return False

    def create_session(self, user_id: str, app_name: str = "app") -> str:
        """Crea una nuova sessione per un utente specifico."""
        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions"
        response = requests.post(url, headers=self.headers, json={"state": {}}, timeout=10)
        response.raise_for_status()
        return response.json()["id"]

    def chat_stream(
        self,
        user_id: str,
        session_id: str,
        message: str,
        app_name: str = "app"
    ) -> Generator[dict[str, Any], None, None]:
        """
        Invia un messaggio all'agente e restituisce un generatore di eventi (SSE).
        """
        url = f"{self.base_url}/run_sse"
        payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}],
            },
            "streaming": True,
        }

        response = requests.post(url, headers=self.headers, json=payload, stream=True, timeout=60)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    yield json.loads(line_str[6:])

    def send_feedback(self, user_id: str, session_id: str, score: int, text: str = "") -> bool:
        """Invia un feedback per la conversazione corrente."""
        url = f"{self.base_url}/feedback"
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "score": score,
            "text": text
        }
        response = requests.post(url, headers=self.headers, json=payload, timeout=10)
        return response.status_code == 200
