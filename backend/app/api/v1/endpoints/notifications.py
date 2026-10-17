"""Notifications & Real-time Alerts endpoint for Assay.

Provides list of unread/read academic milestone, oral defense, and Socratic
dialogue notifications from the persistent store.
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from ....repositories import get_store

router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])


class NotificationItem(BaseModel):
    id: str
    title: str
    description: str
    time: str
    type: str  # 'defense' | 'milestone' | 'socratic'
    isUnread: bool
    actionLabel: Optional[str] = None
    actionUrl: Optional[str] = None


@router.get("", response_model=List[NotificationItem])
async def list_notifications() -> List[NotificationItem]:
    """Retrieve all notifications ordered by most recent first."""
    store = get_store()
    raw = store.list_notifications()
    return [NotificationItem(**n) for n in raw]


@router.post("/mark-read")
async def mark_all_read():
    """Mark all notifications as read."""
    store = get_store()
    store.mark_all_notifications_read()
    return {"status": "ok", "message": "All notifications marked as read"}


@router.post("/{notif_id}/read")
async def mark_single_read(notif_id: str):
    """Mark a specific notification as read."""
    store = get_store()
    found = store.mark_notification_read(notif_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notif_id} not found",
        )
    return {"status": "ok", "notification_id": notif_id}
