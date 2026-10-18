"""F2 — Realtime checklist schemas (API-CONTRACTS section 2.2)."""
from typing import Any, List, Literal, Optional

from pydantic import BaseModel

OriginType = Literal["document", "role_taxonomy", "grounded_external"]


class ChecklistItem(BaseModel):
    item_id: str
    topic: str
    selected: bool = True
    confidence: float
    origin: OriginType
    # DEV 2 addition: True when the engine proposed the item and the student dropped it
    # (app_addons.tag_elective). The PRD allows unchecking, but the contract had no
    # field marking "proposed by the engine, rejected by the student".
    elective: bool = False


class ChecklistGenerateRequest(BaseModel):
    stream: bool = False


class ChecklistResponse(BaseModel):
    session_id: str
    role: str
    source: str
    checklist: List[ChecklistItem]
    engine: Optional[str] = None
    cache: Optional[dict[str, Any]] = None


class ChecklistUpdateRequest(BaseModel):
    selected_item_ids: List[str]


class ChecklistUpdateResponse(BaseModel):
    session_id: str
    status: str = "updated"
    selected_item_ids: List[str]
    # F3 consumes only the selected items; echoing them back proves the write landed.
    checklist: List[ChecklistItem]
    selected_count: int
