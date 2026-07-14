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

import os
import sys

# Aggiunge la radice del progetto al path per permettere l'importazione dei moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import RandstadApiClient


def main():
    """
    Script di esempio per testare le API dell'agente Randstad.
    Dimostra il flusso: Health Check -> Creazione Sessione -> Chat Streaming -> Feedback.
    """
    client = RandstadApiClient()

    print("--- 1. Health Check ---")
    if client.health_check():
        print("✅ API is healthy")
    else:
        print("❌ API is not reachable. Is the server running? (Try 'make local-backend')")
        return

    user_id = "test_user_fix"
    print(f"\n--- 2. Creating Session for {user_id} ---")
    try:
        session_id = client.create_session(user_id)
        print(f"✅ Session created: {session_id}")
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        return

    # Esempio di frase che innesca la qualificazione lead su Firestore
    message = "Ciao! Al momento lavoriamo con un competitor e abbiamo circa 50 lavoratori."
    print(f"\n--- 3. Sending Message: '{message}' ---")
    print("Response: ", end="", flush=True)

    try:
        for event in client.chat_stream(user_id, session_id, message):
            # In ADK, il contenuto testuale è sotto 'content' -> 'parts'
            content = event.get("content")
            if content and content.get("parts"):
                for part in content["parts"]:
                    if part.get("text"):
                        print(part["text"], end="", flush=True)
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")

    print("\n\n--- 4. Sending Feedback ---")
    if client.send_feedback(user_id, session_id, 5, "L'agente ha riconosciuto correttamente il competitor!"):
        print("✅ Feedback sent successfully")
    else:
        print("❌ Failed to send feedback")

if __name__ == "__main__":
    main()
