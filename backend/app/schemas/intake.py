from typing import List, Optional
from pydantic import BaseModel, Field

SEED_ROLES = [
    "Frontend",
    "Backend",
    "Fullstack",
    "DevOps",
    "Data/ML",
    "Mobile",
    "QA/Test",
    "Security",
    "System Design"
]

class RolesResponse(BaseModel):
    roles: List[str] = SEED_ROLES
    others_option: str = "Others"

class IntakeRequest(BaseModel):
    intent: str = Field(..., min_length=3, description="What the user wants to learn")
    role: str = Field(..., description="Role selected from seed list or Others")
    role_is_custom: bool = False
    custom_role: Optional[str] = None
    document: Optional[str] = None

class IntakeResponse(BaseModel):
    session_id: str
    intent: str
    role: str
    has_document: bool
    available_roles: List[str]
    suggested_others: bool = False
    next: str
