from typing import List, Literal
from pydantic import BaseModel

OriginType = Literal["document", "role_taxonomy", "grounded_external"]

class ChecklistItem(BaseModel):
    item_id: str
    topic: str
    selected: bool = True
    confidence: float
    origin: OriginType

class ChecklistGenerateRequest(BaseModel):
    stream: bool = False

class ChecklistResponse(BaseModel):
    session_id: str
    role: str
    source: str
    checklist: List[ChecklistItem]

class ChecklistUpdateRequest(BaseModel):
    selected_item_ids: List[str]
