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

from typing import Any, Optional
import uuid
import time
from google.cloud import firestore
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.base_session_service import GetSessionConfig
from google.adk.sessions.base_session_service import ListSessionsResponse
from google.adk.sessions.session import Session
from google.adk.events.event import Event
from google.adk.sessions.state import State
from google.adk.cli.service_registry import get_service_registry

class FirestoreSessionService(BaseSessionService):
    """
    A Firestore-based implementation of the SessionService.
    
    Persists sessions, events, and state to Google Cloud Firestore.
    structure:
    apps/{app_name} (App State)
    apps/{app_name}/users/{user_id} (User State)
    apps/{app_name}/users/{user_id}/sessions/{session_id} (Session Data + Session State)
    apps/{app_name}/users/{user_id}/sessions/{session_id}/events/{event_id} (Events)
    """

    def __init__(
        self, 
        uri: str,
        **kwargs: Any
    ):
        """
        Args:
            uri: The URI of the session service (e.g., firestore://project-id/database-id).
            **kwargs: Additional arguments like agents_dir.
        """
        # Parsing URI: firestore://project-id/database-id
        # Expected format: firestore://{project}/{database}
        project = None
        database = None
        
        if "://" in uri:
            path = uri.split("://")[1]
            parts = path.split("/")
            if len(parts) >= 1:
                project = parts[0]
            if len(parts) >= 2:
                database = parts[1]

        # Initialize the client
        self._client = firestore.AsyncClient(project=project, database=database)

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        session_id = (
            session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())
        )
        
        session_ref = self._client.collection("apps").document(app_name)\
            .collection("users").document(user_id)\
            .collection("sessions").document(session_id)

        current_time = time.time()
        initial_session_state = state or {}
        
        session_data = {
            "id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "state": initial_session_state,
            "last_update_time": current_time,
        }

        await session_ref.set(session_data)

        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=initial_session_state,
            last_update_time=current_time,
            events=[]
        )

        return await self._merge_state(app_name, user_id, session)

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        session_ref = self._client.collection("apps").document(app_name)\
            .collection("users").document(user_id)\
            .collection("sessions").document(session_id)

        doc_snapshot = await session_ref.get()
        if not doc_snapshot.exists:
            return None

        session_data = doc_snapshot.to_dict()
        session_data["events"] = [] 
        
        try:
            session = Session.model_validate(session_data)
        except Exception:
            session = Session(
                id=session_data.get("id"),
                app_name=session_data.get("app_name"),
                user_id=session_data.get("user_id"),
                state=session_data.get("state", {}),
                last_update_time=session_data.get("last_update_time", 0.0),
                events=[]
            )

        events_ref = session_ref.collection("events")
        query = events_ref.order_by("timestamp")

        if config:
            if config.after_timestamp:
                query = query.where(filter=firestore.FieldFilter("timestamp", ">", config.after_timestamp))
            if config.num_recent_events:
                 query = events_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(config.num_recent_events)
        
        events_snapshots = await query.get()
        
        loaded_events = []
        for snap in events_snapshots:
            event_data = snap.to_dict()
            try:
                event = Event.model_validate(event_data)
                loaded_events.append(event)
            except Exception:
                continue

        if config and config.num_recent_events:
            loaded_events.sort(key=lambda e: e.timestamp)

        session.events = loaded_events
        
        return await self._merge_state(app_name, user_id, session)

    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        sessions_ref = self._client.collection("apps").document(app_name)\
            .collection("users").document(user_id)\
            .collection("sessions")
        
        query = sessions_ref.order_by("last_update_time", direction=firestore.Query.DESCENDING)
        
        snapshots = await query.get()
        sessions_list = []
        
        for snap in snapshots:
            data = snap.to_dict()
            data["events"] = []
            try:
                session = Session.model_validate(data)
                merged_session = await self._merge_state(app_name, user_id, session)
                sessions_list.append(merged_session)
            except Exception:
                continue
                
        return ListSessionsResponse(sessions=sessions_list)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        session_ref = self._client.collection("apps").document(app_name)\
            .collection("users").document(user_id)\
            .collection("sessions").document(session_id)
            
        events_ref = session_ref.collection("events")
        await self._delete_collection(events_ref, batch_size=50)
        await session_ref.delete()

    async def append_event(self, session: Session, event: Event) -> Event:
        if event.partial:
            return event

        self._update_session_state_local(session, event)
        session.events.append(event)
        session.last_update_time = event.timestamp

        batch = self._client.batch()
        
        app_name = session.app_name
        user_id = session.user_id
        session_id = session.id
        
        app_ref = self._client.collection("apps").document(app_name)
        user_ref = app_ref.collection("users").document(user_id)
        session_ref = user_ref.collection("sessions").document(session_id)
        event_ref = session_ref.collection("events").document(event.id)

        event_dict = event.model_dump(mode='json', exclude_none=True)
        batch.set(event_ref, event_dict)

        app_updates = {}
        user_updates = {}
        session_updates = {}

        if event.actions and event.actions.state_delta:
            for key, value in event.actions.state_delta.items():
                if not key or key.startswith(State.TEMP_PREFIX):
                    continue
                
                if key.startswith(State.APP_PREFIX):
                    clean_key = key.removeprefix(State.APP_PREFIX)
                    if clean_key:
                        app_updates[clean_key] = value
                elif key.startswith(State.USER_PREFIX):
                    clean_key = key.removeprefix(State.USER_PREFIX)
                    if clean_key:
                        user_updates[clean_key] = value
                else:
                    session_updates[f"state.{key}"] = value

        if app_updates:
            batch.set(app_ref, app_updates, merge=True)
        
        if user_updates:
            batch.set(user_ref, user_updates, merge=True)

        session_updates["last_update_time"] = session.last_update_time
        batch.update(session_ref, session_updates)

        await batch.commit()
        return event

    async def _merge_state(self, app_name: str, user_id: str, session: Session) -> Session:
        app_ref = self._client.collection("apps").document(app_name)
        app_snap = await app_ref.get()
        if app_snap.exists:
            app_data = app_snap.to_dict()
            for k, v in app_data.items():
                session.state[State.APP_PREFIX + k] = v

        user_ref = app_ref.collection("users").document(user_id)
        user_snap = await user_ref.get()
        if user_snap.exists:
            user_data = user_snap.to_dict()
            for k, v in user_data.items():
                session.state[State.USER_PREFIX + k] = v
                
        return session

    async def _delete_collection(self, coll_ref, batch_size):
        docs = await coll_ref.limit(batch_size).get()
        deleted = 0

        for doc in docs:
            await doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            return await self._delete_collection(coll_ref, batch_size)

    def _update_session_state_local(self, session: Session, event: Event) -> None:
        if not event.actions or not event.actions.state_delta:
            return
        for key, value in event.actions.state_delta.items():
            if key.startswith(State.TEMP_PREFIX):
                continue
            session.state.update({key: value})

def register_firestore_session_service():
    """Registra il servizio di sessione Firestore nel registry ADK."""
    registry = get_service_registry()
    registry.register_session_service("firestore", FirestoreSessionService)
