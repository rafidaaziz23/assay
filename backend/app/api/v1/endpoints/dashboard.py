"""Dashboard Aggregates & Cognitive Load Metrics endpoint.

Implements the multi-subject learning summary, upcoming oral defenses,
recent Socratic probing quotes, and weekly inquiry rhythm.
"""
from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter

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


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary() -> DashboardSummaryResponse:
    """Return comprehensive learner dashboard overview matching Figma node 1:1886."""
    return DashboardSummaryResponse(
        learner_name="Maya Lin",
        headline_subject="Causal Inference",
        remaining_modules=2,
        active_subjects_count=3,
        total_modules_count=18,
        defenses_passed_count=12,
        defenses_month_delta="+3 this month",
        reasoning_depth_pct=88,
        bloom_tier_label="First-Principles (Bloom Level 5)",
        weekly_focus_hours=6.4,
        learning_paths=[
            LearningPathSummary(
                id="lp-1",
                title="Statistics for Decisions: Neyman–Pearson Lemma",
                level_tag="Applied Level",
                module_label="Module 03 · Hypothesis Testing & LRT",
                last_active="42 mins ago",
                concepts_defended="4 of 6 concepts defended",
                progress_pct=66,
                prerequisite_note="Prerequisite: Probability Bounds met",
                action_url="/app/reader",
            ),
            LearningPathSummary(
                id="lp-2",
                title="Causal Inference & Potential Outcomes",
                level_tag="Rigorous Level",
                module_label="Module 02 · Backdoor Criterion & DAGs",
                last_active="Yesterday",
                concepts_defended="1 of 6 concepts defended",
                progress_pct=17,
                prerequisite_note="1 unresolved counter-argument",
                action_url="/app/reader",
            ),
        ],
        recent_inquiries=[
            SocraticInquiryRecord(
                id="inq-1",
                topic="Monotone Likelihood",
                time="Today, 10:15 AM",
                badge_status="Mastered",
                question_quote="If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?",
                resolution_theorem="Karlin-Rubin Theorem",
            ),
            SocraticInquiryRecord(
                id="inq-2",
                topic="Causal DAGs",
                time="Oct 22, 16:40",
                badge_status="In Progress",
                question_quote="Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?",
                resolution_theorem="Asymptotic bias vs variance distinction",
            ),
            SocraticInquiryRecord(
                id="inq-3",
                topic="LNP Formulation",
                time="Oct 20, 11:20",
                badge_status="Mastered",
                question_quote="How does the mRNA lipid nanoparticle avoid early endosomal degradation?",
                resolution_theorem="Ionizable lipids and pH-triggered endosomal escape",
            ),
        ],
        upcoming_defense=UpcomingDefenseInfo(
            title="Neyman–Pearson LRT & Error Bounds",
            subtitle="Module 03 Capstone Validation",
            scheduled_time="Tomorrow at 10:00 AM",
            examiner_name="Dr. Julian Vance",
            examiner_role="Lead Examiner · Decision Theory",
            examiner_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            description="45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.",
        ),
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
