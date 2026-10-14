"""
Chapter Lifecycle State Machine:
LOCKED -> ACTIVE_READING -> INTERVIEW -> SCORED -> UNLOCKED (>=75) / NEEDS_REVIEW (<75)
"""
from typing import Dict, Any, Optional

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.syllabi: Dict[str, Dict[str, Any]] = {}
        self.chapters: Dict[str, Dict[str, Any]] = {}
        self.interviews: Dict[str, Dict[str, Any]] = {}
        self.focus_events: Dict[str, list] = {}
        self.appeals: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str, intent: str, role: str, has_doc: bool) -> Dict[str, Any]:
        data = {
            "session_id": session_id,
            "intent": intent,
            "role": role,
            "has_doc": has_doc,
            "checklist": [],
            "syllabus_id": None
        }
        self.sessions[session_id] = data
        return data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def set_chapter_status(self, chapter_id: str, new_status: str):
        if chapter_id in self.chapters:
            self.chapters[chapter_id]["status"] = new_status

    def unlock_next_chapter(self, current_chapter_id: str) -> Optional[str]:
        # Find current chapter order
        curr = self.chapters.get(current_chapter_id)
        if not curr:
            return None
        curr_order = curr.get("order", 1)
        next_order = curr_order + 1
        
        # Find next chapter
        for ch_id, ch in self.chapters.items():
            if ch.get("order") == next_order:
                ch["status"] = "ACTIVE_READING"
                ch["next_locked"] = False
                return ch_id
        return None

# Singleton session store
store = SessionStore()
