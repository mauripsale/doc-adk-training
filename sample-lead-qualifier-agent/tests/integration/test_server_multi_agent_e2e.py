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
import requests
import pytest
from tests.integration.test_server_e2e import BASE_URL, STREAM_URL, HEADERS, server_fixture

def test_e2e_multi_agent_delegation(server_fixture):
    """
    Test E2E che verifica la risposta del server e la capacità di rispondere 
    quando viene menzionata un'azienda (innescando potenzialmente il ricercatore).
    """
    user_id = "e2e_multi_agent_user"
    
    # 1. Crea sessione
    session_url = f"{BASE_URL}/apps/app/users/{user_id}/sessions"
    session_response = requests.post(session_url, headers=HEADERS, json={}, timeout=60)
    assert session_response.status_code == 200
    session_id = session_response.json()["id"]

    # 2. Invia messaggio
    data = {
        "app_name": "app",
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": "Lavoro per Ferrero Spa"}],
        },
        "streaming": True,
    }

    response = requests.post(STREAM_URL, headers=HEADERS, json=data, stream=True, timeout=60)
    assert response.status_code == 200

    events = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode("utf-8")
            if line_str.startswith("data: "):
                event = json.loads(line_str[6:])
                events.append(event)

    # 3. Verifica che ci sia stata una risposta testuale (frutto della ricerca o del root agent)
    has_text = any(
        part.get("text")
        for e in events if e.get("content")
        for part in e["content"].get("parts", [])
    )
    
    assert has_text, "Il server non ha prodotto alcuna risposta alla menzione dell'azienda."
