from typing import Any, Optional
import uuid
import time
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService, GetSessionConfig, ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.events.event import Event

class FirestoreSessionService(BaseSessionService):
    def __init__(self, project_id: str):
        self._client = firestore.AsyncClient(project=project_id)

    async def create_session(self, *, app_name: str, user_id: str, state: Optional[dict] = None, session_id: Optional[str] = None) -> Session:
        sid = session_id or str(uuid.uuid4())
        return Session(id=sid, app_name=app_name, user_id=user_id, state=state or {})

    async def get_session(self, config: GetSessionConfig) -> Optional[Session]:
        return await self.create_session(app_name=config.app_name, user_id=config.user_id, session_id=config.session_id)

    async def append_event(self, event: Event, session: Session) -> None:
        print(f"🔥 [Firestore] Appending event: {event.author}")

    async def update_session_state(self, session: Session) -> None:
        print(f"🔥 [Firestore] Syncing state for session: {session.id}")

    async def list_sessions(self, app_name: str, user_id: str) -> ListSessionsResponse:
        return ListSessionsResponse(sessions=[])

    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        pass
