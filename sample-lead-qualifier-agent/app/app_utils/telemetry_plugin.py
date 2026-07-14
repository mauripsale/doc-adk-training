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

from typing import Any, Optional, TYPE_CHECKING
from opentelemetry import trace
from google.adk.plugins.base_plugin import BasePlugin

if TYPE_CHECKING:
    from google.adk.agents.invocation_context import InvocationContext

class SessionTelemetryPlugin(BasePlugin):
    """
    Un plugin globale per iniettare attributi custom di telemetria (come il session_id)
    nello span radice 'invocation' di OpenTelemetry.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name=kwargs.get("name", "session_telemetry_plugin"))

    async def before_run_callback(
        self, *, invocation_context: "InvocationContext"
    ) -> Optional[None]:
        """
        Intercetta l'inizio dell'intera invocazione (prima degli agenti) e 
        aggiunge il session_id allo span 'invocation' di OpenTelemetry.
        """
        current_span = trace.get_current_span()
        
        if current_span and current_span.is_recording():
            session_id = invocation_context.session.id
            if session_id:
                current_span.set_attribute("app.session_id", session_id)
                
            user_id = invocation_context.session.user_id
            if user_id:
                current_span.set_attribute("app.user_id", user_id)

        return None
