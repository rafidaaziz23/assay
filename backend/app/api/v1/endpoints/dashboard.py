"""Dashboard Aggregates & Cognitive Load Metrics endpoint.

Implements the multi-subject learning summary, upcoming oral defenses,
recent Socratic probing quotes, and weekly inquiry rhythm.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class LearningPathSummary(BaseModel):
    id: str
    title: str
    level_tag: str
    module_label: str
    last_active: str
    concepts_defended: str
    progress_pct: int
    prerequisite_note: str
    action_url: str


class SocraticInquiryRecord(BaseModel):
    id: str
    topic: str
    time: str
    badge_status: str
    question_quote: str
    resolution_theorem: str


class UpcomingDefenseInfo(BaseModel):
    title: str
    subtitle: str
    scheduled_time: str
    examiner_name: str
    examiner_role: str
    examiner_avatar: str
    description: str


class DayRhythm(BaseModel):
    day: str
    height_pct: str
    active: bool


class DashboardSummaryResponse(BaseModel):
    learner_name: str
    headline_subject: str
    remaining_modules: int
    active_subjects_count: int
    total_modules_count: int
    defenses_passed_count: int
    defenses_month_delta: str
    reasoning_depth_pct: int
    bloom_tier_label: str
    weekly_focus_hours: float
    learning_paths: List[LearningPathSummary]
    recent_inquiries: List[SocraticInquiryRecord]
    upcoming_defense: UpcomingDefenseInfo
    weekly_rhythm: List[DayRhythm]


from ....repositories import get_store
from ....core.seeder import seed_store


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    session_id: Optional[str] = Query(None),
) -> DashboardSummaryResponse:
    """Return comprehensive learner dashboard overview matching Figma node 1:1886."""
    store = get_store()
    if not store.chapters or "ch_algo_01" not in store.chapters:
        seed_store(store)

    # 1. Resolve Active Session
    target_sid = session_id or "sess_coding_basic"
    session = store.get_session(target_sid)
    if not session:
        session = store.get_session("sess_a1b2c3") or (next(iter(store.sessions.values())) if store.sessions else None)
    sid = session["session_id"] if session else "sess_coding_basic"
    chapters = store.session_chapters(sid)

    # 2. Build Multi-Track Learning Paths across all curricula
    learning_paths: List[LearningPathSummary] = []
    # Add active track's chapters first
    for idx, ch in enumerate(chapters[:3]):
        st = ch.get("status", "LOCKED")
        is_active = st in ("ACTIVE_READING", "INTERVIEW")
        is_done = st in ("COMPLETED", "SCORED", "UNLOCKED")
        pct = 66 if is_active else (100 if is_done else (17 if idx == 1 else 0))
        defended = (
            "4 of 6 concepts defended"
            if is_active
            else ("1 of 6 concepts defended" if idx == 1 else ("6 of 6 concepts defended" if is_done else "0 of 6 concepts defended"))
        )
        level = "Applied Level" if idx % 2 == 0 else "Rigorous Level"
        note = (
            "Prerequisite: Core Bounds met"
            if idx == 0
            else ("1 unresolved counter-argument" if idx == 1 else "Prerequisite pending")
        )
        learning_paths.append(
            LearningPathSummary(
                id=ch.get("chapter_id"),
                title=ch.get("title", f"Module 0{idx+1}"),
                level_tag=level,
                module_label=f"Module 0{ch.get('order', idx+1)} · {ch.get('title', '')[:32]}",
                last_active="42 mins ago" if idx == 0 else ("Yesterday" if idx == 1 else "3 days ago"),
                concepts_defended=defended,
                progress_pct=pct,
                prerequisite_note=note,
                action_url="/app/reader",
            )
        )

    # Also include the other track if present so learner can explore both
    other_sids = [s for s in ("sess_coding_basic", "sess_a1b2c3") if s != sid and s in store.sessions]
    for other_sid in other_sids:
        other_chs = store.session_chapters(other_sid)
        if other_chs:
            lead = other_chs[0]
            other_session = store.get_session(other_sid)
            s_title = (other_session.get("syllabus_title") or lead.get("title", "Curriculum Track"))
            learning_paths.append(
                LearningPathSummary(
                    id=lead.get("chapter_id"),
                    title=s_title,
                    level_tag="Rigorous Level",
                    module_label=f"Module 01 · {lead.get('title', '')[:32]}",
                    last_active="Active Track",
                    concepts_defended="2 of 6 concepts defended",
                    progress_pct=33,
                    prerequisite_note="Ready to resume inquiry",
                    action_url="/app/roadmap",
                )
            )

    remaining_modules = len([c for c in chapters if c.get("status") not in ("COMPLETED", "SCORED")]) or 2
    total_modules_count = len(chapters) or 6
    headline = (session.get("syllabus_title") or session.get("intent") or "Algorithms & Data Structures") if session else "Algorithms & Data Structures"
    if len(headline) > 40:
        headline = headline[:37] + "..."

    upcoming_title = "Algorithmic Complexity & Asymptotic Bounds"
    upcoming_sub = "Module 01 Capstone Defense"
    if chapters:
        active_ch = next((c for c in chapters if c.get("status") == "ACTIVE_READING"), chapters[0])
        upcoming_title = active_ch.get("title", upcoming_title)
        upcoming_sub = f"Module 0{active_ch.get('order', 1)} Dialectic Defense"

    raw_inquiries = store.list_inquiries()
    recent_inquiries = [
        SocraticInquiryRecord(**inq) for inq in raw_inquiries[:4]
    ] if raw_inquiries else [
        SocraticInquiryRecord(
            id="inq-algo-1",
            topic="Asymptotic Notation",
            time="Today, 10:15 AM",
            badge_status="Mastered",
            question_quote="Why is O(n log n) the information-theoretic lower bound for comparison sorts?",
            resolution_theorem="Decision Tree Height & Stirling's Approximation",
        ),
        SocraticInquiryRecord(
            id="inq-1",
            topic="Monotone Likelihood",
            time="Yesterday, 16:40",
            badge_status="Mastered",
            question_quote="If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?",
            resolution_theorem="Karlin-Rubin Theorem",
        ),
        SocraticInquiryRecord(
            id="inq-2",
            topic="Causal DAGs",
            time="Oct 22, 11:20",
            badge_status="In Progress",
            question_quote="Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?",
            resolution_theorem="Asymptotic bias vs variance distinction",
        ),
    ]

    raw_defenses = store.list_defenses()
    if raw_defenses:
        upcoming_defense = UpcomingDefenseInfo(**raw_defenses[0])
    else:
        upcoming_defense = UpcomingDefenseInfo(
            title=upcoming_title,
            subtitle=upcoming_sub,
            scheduled_time="Tomorrow at 10:00 AM",
            examiner_name="Dr. Julian Vance",
            examiner_role="Lead Examiner · Decision Theory",
            examiner_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            description="45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.",
        )

    return DashboardSummaryResponse(
        learner_name="Maya Lin",
        headline_subject=headline,
        remaining_modules=remaining_modules,
        active_subjects_count=3,
        total_modules_count=total_modules_count,
        defenses_passed_count=12,
        defenses_month_delta="+3 this month",
        reasoning_depth_pct=88,
        bloom_tier_label="First-Principles (Bloom Level 5)",
        weekly_focus_hours=6.4,
        learning_paths=learning_paths,
        recent_inquiries=recent_inquiries,
        upcoming_defense=upcoming_defense,
        weekly_rhythm=[
            DayRhythm(day="Mon", height_pct="60%", active=False),
            DayRhythm(day="Tue", height_pct="45%", active=False),
            DayRhythm(day="Wed", height_pct="85%", active=True),
            DayRhythm(day="Thu", height_pct="70%", active=False),
            DayRhythm(day="Fri", height_pct="95%", active=False),
            DayRhythm(day="Sat", height_pct="30%", active=False),
            DayRhythm(day="Sun", height_pct="50%", active=False),
        ],
    )

