"""Firestore repository implementation and sync engine for Assay.

Supports:
1. Direct connection via service account JSON (FIREBASE_CREDENTIALS_PATH or GOOGLE_APPLICATION_CREDENTIALS).
2. Automatic discovery of backend/data/serviceAccountKey.json.
3. Dual-mode FirestoreStore that keeps fast in-memory state while persisting to Firestore collections.
4. Batch seeder sync (sync_store_to_firestore) to upload full demonstration datasets to Firebase.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import InMemoryStore

logger = logging.getLogger("assay.firestore")

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DATA_DIR = _BACKEND_DIR / "data"
_ROOT_DIR = _BACKEND_DIR.parent

_CANDIDATE_DIRS = [
    _ROOT_DIR,
    _BACKEND_DIR,
    _DATA_DIR,
    Path("."),
]


def resolve_credentials_path(custom_path: Optional[str] = None) -> Optional[Path]:
    """Locate service account credentials JSON file."""
    if custom_path and Path(custom_path).exists():
        return Path(custom_path).resolve()

    env_path = os.environ.get("FIREBASE_CREDENTIALS_PATH") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and Path(env_path).exists():
        return Path(env_path).resolve()

    patterns = ["*firebase-adminsdk*.json", "*serviceAccountKey*.json", "serviceAccountKey.json", "credentials.json"]
    for d in _CANDIDATE_DIRS:
        if not d.exists():
            continue
        for pat in patterns:
            matches = list(d.glob(pat))
            if matches:
                return matches[0].resolve()

    return None


def get_firestore_client(
    credentials_path: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Any:
    """Initialize and return a google.cloud.firestore.Client instance."""
    resolved_path = resolve_credentials_path(credentials_path)

    if not resolved_path and not project_id and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise FileNotFoundError(
            "No Firebase service account key found. Please place serviceAccountKey.json in "
            "backend/data/serviceAccountKey.json or set FIREBASE_CREDENTIALS_PATH."
        )

    # 1. Try via firebase_admin
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            if resolved_path:
                cred = credentials.Certificate(str(resolved_path))
                firebase_admin.initialize_app(cred, {"projectId": project_id} if project_id else None)
            else:
                firebase_admin.initialize_app()
        return firestore.client()
    except Exception as e_admin:
        logger.debug("firebase_admin initialization fallback: %s", e_admin)

    # 2. Try via google.cloud.firestore directly
    try:
        from google.cloud import firestore

        if resolved_path:
            return firestore.Client.from_service_account_json(str(resolved_path), project=project_id)
        if project_id:
            return firestore.Client(project=project_id)
        return firestore.Client()
    except Exception as e_client:
        raise RuntimeError(
            f"Unable to initialize Firestore client. "
            f"Please verify serviceAccountKey.json is placed in backend/data/ or FIREBASE_CREDENTIALS_PATH is set. "
            f"Details: {e_client}"
        ) from e_client


class FirestoreStore(InMemoryStore):
    """Dual-mode store: reads from memory cache, persists writes to both memory and Firestore."""

    def __init__(self, project_id: Optional[str] = None, client: Any = None) -> None:
        super().__init__()
        self.project_id = project_id
        self.client = client
        if self.client is None:
            try:
                self.client = get_firestore_client(project_id=project_id)
            except Exception as e:
                logger.warning("Firestore client unavailable, continuing with local persistence: %s", e)

    def create_session(self, session_id: str, **fields: Any) -> Dict[str, Any]:
        data = super().create_session(session_id, **fields)
        if self.client:
            try:
                self.client.collection("sessions").document(session_id).set(data, merge=True)
            except Exception as e:
                logger.warning("Firestore write failed for session %s: %s", session_id, e)
        return data

    def update_session(self, session_id: str, **fields: Any) -> Optional[Dict[str, Any]]:
        data = super().update_session(session_id, **fields)
        if self.client and data:
            try:
                self.client.collection("sessions").document(session_id).set(data, merge=True)
            except Exception as e:
                logger.warning("Firestore update failed for session %s: %s", session_id, e)
        return data

    def put_chapter(self, chapter: Dict[str, Any]) -> Dict[str, Any]:
        data = super().put_chapter(chapter)
        if self.client:
            cid = chapter.get("chapter_id")
            if cid:
                try:
                    self.client.collection("chapters").document(cid).set(data, merge=True)
                except Exception as e:
                    logger.warning("Firestore write failed for chapter %s: %s", cid, e)
        return data

    def save_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        data = super().save_user(user)
        if self.client:
            uid = user.get("id")
            if uid:
                try:
                    self.client.collection("users").document(uid).set(data, merge=True)
                except Exception as e:
                    logger.warning("Firestore write failed for user %s: %s", uid, e)
        return data

    def add_notification(self, notif: Dict[str, Any]) -> Dict[str, Any]:
        data = super().add_notification(notif)
        if self.client:
            nid = notif.get("id")
            if nid:
                try:
                    self.client.collection("notifications").document(nid).set(data, merge=True)
                except Exception as e:
                    logger.warning("Firestore write failed for notification %s: %s", nid, e)
        return data

    def add_inquiry(self, inquiry: Dict[str, Any]) -> Dict[str, Any]:
        data = super().add_inquiry(inquiry)
        if self.client:
            try:
                self.client.collection("inquiries").add(data)
            except Exception as e:
                logger.warning("Firestore write failed for inquiry: %s", e)
        return data

    def add_defense(self, defense: Dict[str, Any]) -> Dict[str, Any]:
        data = super().add_defense(defense)
        if self.client:
            try:
                self.client.collection("defenses").add(data)
            except Exception as e:
                logger.warning("Firestore write failed for defense: %s", e)
        return data


def sync_store_to_firestore(store: InMemoryStore, client: Any = None) -> Dict[str, int]:
    """Upload all entities from an InMemoryStore into Firestore collections using batches."""
    if client is None:
        client = get_firestore_client()

    stats: Dict[str, int] = {
        "users": 0,
        "sessions": 0,
        "chapters": 0,
        "notifications": 0,
        "inquiries": 0,
        "defenses": 0,
    }

    # 1. Users Collection
    batch = client.batch()
    op_count = 0
    for uid, user in store.users.items():
        doc_ref = client.collection("users").document(uid)
        batch.set(doc_ref, user, merge=True)
        stats["users"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    # 2. Sessions Collection
    batch = client.batch()
    op_count = 0
    for sid, sdata in store.sessions.items():
        doc_ref = client.collection("sessions").document(sid)
        batch.set(doc_ref, sdata, merge=True)
        stats["sessions"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    # 3. Chapters Collection
    batch = client.batch()
    op_count = 0
    for cid, cdata in store.chapters.items():
        doc_ref = client.collection("chapters").document(cid)
        batch.set(doc_ref, cdata, merge=True)
        stats["chapters"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    # 4. Notifications Collection
    batch = client.batch()
    op_count = 0
    for notif in store.notifications:
        nid = notif.get("id")
        doc_ref = client.collection("notifications").document(nid) if nid else client.collection("notifications").document()
        batch.set(doc_ref, notif, merge=True)
        stats["notifications"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    # 5. Inquiries Collection
    batch = client.batch()
    op_count = 0
    for inq in store.inquiries:
        doc_ref = client.collection("inquiries").document()
        batch.set(doc_ref, inq, merge=True)
        stats["inquiries"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    # 6. Defenses Collection
    batch = client.batch()
    op_count = 0
    for def_item in store.defenses:
        doc_ref = client.collection("defenses").document()
        batch.set(doc_ref, def_item, merge=True)
        stats["defenses"] += 1
        op_count += 1
        if op_count >= 400:
            batch.commit()
            batch = client.batch()
            op_count = 0
    if op_count > 0:
        batch.commit()

    return stats


def build_store(project_id: Optional[str] = None) -> InMemoryStore:
    """Factory: FirestoreStore when credentials exist and client connects, InMemoryStore otherwise."""
    resolved_path = resolve_credentials_path()
    if not resolved_path and not project_id:
        return InMemoryStore()

    try:
        client = get_firestore_client(project_id=project_id)
        return FirestoreStore(project_id=project_id, client=client)
    except Exception as e:
        logger.info("Firestore unavailable, fallback to InMemoryStore: %s", e)
        return InMemoryStore()
