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
import subprocess
import sys

# Aggiunge la radice del progetto al path per permettere l'importazione dei moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import RandstadApiClient


def get_gcloud_output(command: list) -> str:
    """Esegue un comando gcloud e restituisce l'output pulito."""
    try:
        return subprocess.check_output(command).decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di gcloud: {e}")
        sys.exit(1)

def main():
    """
    Script per testare l'agente Randstad deployato su Cloud Run.
    Recupera automaticamente URL e ID Token tramite gcloud.
    """
    # Parametri di configurazione (modifica se necessario)
    service_name = "randstad-adk-dev"
    region = "us-central1"

    print(f"--- 0. Fetching Cloud Run details for {service_name} ---")

    # 1. Recupera l'URL del servizio
    print("Fetching Service URL...")
    url = get_gcloud_output([
        "gcloud", "run", "services", "describe", service_name,
        "--platform", "managed", "--region", region, "--format", "value(status.url)"
    ])
    print(f"✅ Service URL: {url}")

    # 2. Genera un ID Token per l'autenticazione
    print("Generating ID Token...")
    token = get_gcloud_output(["gcloud", "auth", "print-identity-token"])
    print("✅ ID Token generated")

    # 3. Inizializza il client con il token
    client = RandstadApiClient(base_url=url, token=token)

    print("\n--- 1. Health Check ---")
    if client.health_check():
        print("✅ Cloud Run API is healthy")
    else:
        print("❌ Cloud Run API is not reachable.")
        return

    user_id = "cloud_run_tester"
    print(f"\n--- 2. Creating Session for {user_id} ---")
    try:
        session_id = client.create_session(user_id)
        print(f"✅ Session created: {session_id}")
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        return

    message = "Buongiorno, lavoro con Manpower e abbiamo 25 lavoratori somministrati."
    print(f"\n--- 3. Sending Message: '{message}' ---")
    print("Response: ", end="", flush=True)

    try:
        for event in client.chat_stream(user_id, session_id, message):
            content = event.get("content")
            if content and content.get("parts"):
                for part in content["parts"]:
                    if part.get("text"):
                        print(part["text"], end="", flush=True)
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")

    print("\n\n--- 4. Sending Feedback ---")
    if client.send_feedback(user_id, session_id, 5, "Test su Cloud Run completato con successo!"):
        print("✅ Feedback sent successfully")
    else:
        print("❌ Failed to send feedback")

if __name__ == "__main__":
    main()
