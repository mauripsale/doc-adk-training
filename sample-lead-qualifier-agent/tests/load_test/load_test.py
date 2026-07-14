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
import logging
import os
import time
import uuid

import urllib3
from locust import HttpUser, between, task

# Suppress InsecureRequestWarning if SSL verification is disabled
if os.environ.get("LOCUST_SKIP_CERT_VERIFY", "").lower() == "true":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ENDPOINT = "/run_sse"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChatStreamUser(HttpUser):
    """Simulates a user interacting with the multi-agent B2B qualifier."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def send_message(self, user_id, session_id, message_text, name_prefix, headers, verify_ssl):
        """Helper to send a message, handle SSE response, and track latencies."""
        data = {
            "app_name": "app",
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message_text}],
            },
            "streaming": True,
        }
        start_time = time.time()

        with self.client.post(
            ENDPOINT,
            name=f"{name_prefix} (trigger)",
            headers=headers,
            json=data,
            catch_response=True,
            stream=True,
            params={"alt": "sse"},
            verify=verify_ssl,
        ) as response:
            if response.status_code == 200:
                full_content = ""
                has_error = False
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        clean_line = line_str[6:] if line_str.startswith("data: ") else line_str
                        try:
                            event_data = json.loads(clean_line)
                            
                            if isinstance(event_data, dict):
                                if "text" in event_data:
                                    full_content += event_data["text"]
                                
                                # Check for logic error codes in the SSE stream
                                if event_data.get("code", 0) >= 400:
                                    has_error = True
                                    response.failure(f"Agent Logic Error: {event_data.get('message')}")
                        except json.JSONDecodeError:
                            pass

                total_time = (time.time() - start_time) * 1000

                if not has_error:
                    # Fire a custom event for the full processing cycle (AI reasoning + tool execution)
                    self.environment.events.request.fire(
                        request_type="AI_FLOW",
                        name=f"{name_prefix} (full cycle)",
                        response_time=total_time,
                        response_length=len(full_content),
                        response=response,
                        context={},
                    )
                return not has_error
            else:
                error_msg = f"HTTP {response.status_code}: {response.reason}"
                if response.status_code == 0:
                    err = getattr(response, "error", None)
                    if err:
                        error_msg += f" - Exception: {err}"
                response.failure(error_msg)
                return False

    @task
    def chat_stream(self) -> None:
        """Simulates a complete multi-agent interaction flow: Research -> Qualification -> Save."""
        headers = {"Content-Type": "application/json"}
        if os.environ.get("_ID_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['_ID_TOKEN']}"

        # SSL Verification toggle
        verify_ssl = os.environ.get("LOCUST_SKIP_CERT_VERIFY", "").lower() != "true"

        # 1. Create session
        user_id = f"user_{uuid.uuid4()}"
        session_data = {"state": {"preferred_language": "Italian", "visit_count": 1}}

        with self.client.post(
            f"/apps/app/users/{user_id}/sessions",
            headers=headers,
            json=session_data,
            verify=verify_ssl,
            catch_response=True,
            name="Step 0: Create Session"
        ) as session_response:
            if session_response.status_code not in [200, 201]:
                error_msg = f"Failed to create session: {session_response.status_code}"
                session_response.failure(error_msg)
                return
            try:
                session_id = session_response.json()["id"]
            except:
                session_response.failure("Invalid session JSON")
                return

        # 2. Step 1: Identify Company (triggers Researcher)
        success = self.send_message(
            user_id, session_id, 
            "Buongiorno, lavoro per la ditta Rossi Srl.", 
            "Step 1: Research", 
            headers, verify_ssl
        )
        if not success:
            return

        # Human-like delay
        time.sleep(2)

        # 3. Step 2: Qualify and Save (triggers Firestore tool)
        # Note: Functional success is verified via Firestore logs on the server side.
        self.send_message(
            user_id, session_id, 
            "Sì, usiamo dei collaboratori esterni e abbiamo circa 50 lavoratori.", 
            "Step 2: Save to Firestore", 
            headers, verify_ssl
        )
