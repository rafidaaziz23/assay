import {
  RolesResponse,
  IntakeRequest,
  IntakeResponse,
  ChecklistResponse,
  SyllabusResponse,
  ChapterDetailResponse,
  SocraticAskRequest,
  SocraticAskResponse,
  SuggestionsResponse,
  InterviewStartResponse,
  InterviewTurnRequest,
  InterviewTurnResponse,
  InterviewFinalizeResponse,
  CalibrationResponse,
  FocusEventsResponse,
  FinalReportResponse,
  LoginResponse,
  UserProfile,
  DocumentUploadResponse,
  DashboardSummaryResponse,
  SettingsPayload
} from '../types/api';

import rolesMock from '../mocks/roles.json';
import intakeMock from '../mocks/intake_created.json';
import checklistMock from '../mocks/checklist.json';
import syllabusMock from '../mocks/syllabus.json';
import chapter01Mock from '../mocks/chapter_01.json';
import socraticReplyMock from '../mocks/socratic_reply.json';
import suggestionsMock from '../mocks/suggestions.json';
import interviewStartMock from '../mocks/interview_start.json';
import interviewTurnMock from '../mocks/interview_turn.json';
import interviewFinalizeMock from '../mocks/interview_finalize.json';
import calibrationMock from '../mocks/calibration.json';
import reportMock from '../mocks/report.json';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE || 'live';

async function request<T>(endpoint: string, options?: RequestInit, mockFallback?: T): Promise<T> {
  if (USE_MOCK && mockFallback !== undefined) {
    return Promise.resolve(mockFallback);
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'x-demo-mode': DEMO_MODE,
        ...(options?.headers || {})
      }
    });

    if (!res.ok) {
      if (mockFallback !== undefined) {
        console.warn(`[Assay API] Endpoint ${endpoint} returned ${res.status}. Falling back to mock data.`);
        return mockFallback;
      }
      throw new Error(`API error ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    if (mockFallback !== undefined) {
      console.warn(`[Assay API] Network error on ${endpoint}. Zero-blocker fallback activated.`, err);
      return mockFallback;
    }
    throw err;
  }
}

export const api = {
  getRoles: () => request<RolesResponse>('/roles', { method: 'GET' }, rolesMock as RolesResponse),

  createIntake: (data: IntakeRequest) =>
    request<IntakeResponse>(
      '/intake',
      {
        method: 'POST',
        body: JSON.stringify(data)
      },
      { ...intakeMock, intent: data.intent, role: data.role } as IntakeResponse
    ),

  getChecklist: (sessionId: string) =>
    request<ChecklistResponse>(
      `/intake/${sessionId}/checklist`,
      { method: 'POST', body: JSON.stringify({ stream: false }) },
      checklistMock as ChecklistResponse
    ),

  updateChecklist: (sessionId: string, selectedIds: string[]) =>
    request<{ status: string }>(
      `/intake/${sessionId}/checklist`,
      {
        method: 'PUT',
        body: JSON.stringify({ selected_item_ids: selectedIds })
      },
      { status: 'updated' }
    ),

  generateSyllabus: (sessionId: string) =>
    request<SyllabusResponse>(
      `/intake/${sessionId}/syllabus`,
      { method: 'POST', body: JSON.stringify({ enable_search_grounding: false }) },
      syllabusMock as SyllabusResponse
    ),

  getSyllabus: (sessionId: string) =>
    request<SyllabusResponse>(
      `/intake/${sessionId}/syllabus`,
      { method: 'GET' },
      syllabusMock as SyllabusResponse
    ),

  getChapter: (chapterId: string) =>
    request<ChapterDetailResponse>(
      `/chapters/${chapterId}`,
      { method: 'GET' },
      chapter01Mock as ChapterDetailResponse
    ),

  socraticAsk: (chapterId: string, data: SocraticAskRequest) =>
    request<SocraticAskResponse>(
      `/chapters/${chapterId}/ask`,
      { method: 'POST', body: JSON.stringify(data) },
      socraticReplyMock as SocraticAskResponse
    ),

  getSuggestions: (chapterId: string, selection: string) =>
    request<SuggestionsResponse>(
      `/chapters/${chapterId}/suggestions?selection=${encodeURIComponent(selection)}`,
      { method: 'GET' },
      suggestionsMock as SuggestionsResponse
    ),

  startInterview: (chapterId: string, sessionId: string) =>
    request<InterviewStartResponse>(
      `/chapters/${chapterId}/interview/start`,
      { method: 'POST', body: JSON.stringify({ session_id: sessionId }) },
      interviewStartMock as InterviewStartResponse
    ),

  interviewTurn: (chapterId: string, data: InterviewTurnRequest) =>
    request<InterviewTurnResponse>(
      `/chapters/${chapterId}/interview/turn`,
      { method: 'POST', body: JSON.stringify(data) },
      interviewTurnMock as InterviewTurnResponse
    ),

  finalizeInterview: (chapterId: string, interviewId: string, finalResponse: string) =>
    request<InterviewFinalizeResponse>(
      `/chapters/${chapterId}/interview/finalize`,
      {
        method: 'POST',
        body: JSON.stringify({ interview_id: interviewId, final_response: finalResponse })
      },
      interviewFinalizeMock as InterviewFinalizeResponse
    ),

  submitCalibration: (chapterId: string, interviewId: string, predictedScore: number) =>
    request<CalibrationResponse>(
      `/chapters/${chapterId}/calibration`,
      {
        method: 'POST',
        body: JSON.stringify({ interview_id: interviewId, predicted_score: predictedScore })
      },
      calibrationMock as CalibrationResponse
    ),

  sendFocusEvents: (chapterId: string, interviewId: string, events: any[]) =>
    request<FocusEventsResponse>(
      `/chapters/${chapterId}/focus-events`,
      {
        method: 'POST',
        body: JSON.stringify({
          interview_id: interviewId,
          events,
          video_transmitted: false
        })
      },
      {
        integrity_flag: events.length > 0 ? 'assisted' : 'clean',
        auto_blur: events.length > 0,
        summary: { gaze_drift_count: 0, multi_face_count: 0, tab_blur_count: 0 }
      }
    ),

  getFinalReport: (sessionId: string) =>
    request<FinalReportResponse>(
      `/report/${sessionId}`,
      { method: 'GET' },
      reportMock as FinalReportResponse
    ),

  login: (email: string, password: string) =>
    request<LoginResponse>(
      '/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      },
      {
        access_token: 'mock_token_maya',
        token_type: 'bearer',
        expires_in: 86400,
        user: {
          id: 'usr_89214a',
          name: 'Maya Lin',
          email: 'maya.lin@stanford.edu',
          role: 'Fellow',
          handle: '@mayalin',
          institution: 'Stanford University',
          streak_days: 14,
          credits: 1250,
          avatar_url:
            'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
        },
      }
    ),

  getCurrentUser: () =>
    request<UserProfile>(
      '/auth/me',
      { method: 'GET' },
      {
        id: 'usr_89214a',
        name: 'Maya Lin',
        email: 'maya.lin@stanford.edu',
        role: 'Fellow',
        handle: '@mayalin',
        institution: 'Stanford University',
        streak_days: 14,
        credits: 1250,
        avatar_url:
          'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
      }
    ),

  getDashboardSummary: (sessionId?: string) =>
    request<DashboardSummaryResponse>(
      sessionId ? `/dashboard/summary?session_id=${sessionId}` : '/dashboard/summary',
      { method: 'GET' },
      {
        learner_name: 'Maya Lin',
        headline_subject: 'Causal Inference',
        remaining_modules: 2,
        active_subjects_count: 3,
        total_modules_count: 18,
        defenses_passed_count: 12,
        defenses_month_delta: '+3 this month',
        reasoning_depth_pct: 88,
        bloom_tier_label: 'First-Principles (Bloom Level 5)',
        weekly_focus_hours: 6.4,
        learning_paths: [
          {
            id: 'lp-1',
            title: 'Statistics for Decisions: Neyman–Pearson Lemma',
            level_tag: 'Applied Level',
            module_label: 'Module 03 · Hypothesis Testing & LRT',
            last_active: '42 mins ago',
            concepts_defended: '4 of 6 concepts defended',
            progress_pct: 66,
            prerequisite_note: 'Prerequisite: Probability Bounds met',
            action_url: '/app/reader',
          },
          {
            id: 'lp-2',
            title: 'Causal Inference & Potential Outcomes',
            level_tag: 'Rigorous Level',
            module_label: 'Module 02 · Backdoor Criterion & DAGs',
            last_active: 'Yesterday',
            concepts_defended: '1 of 6 concepts defended',
            progress_pct: 17,
            prerequisite_note: '1 unresolved counter-argument',
            action_url: '/app/reader',
          },
        ],
        recent_inquiries: [
          {
            id: 'inq-1',
            topic: 'Monotone Likelihood',
            time: 'Today, 10:15 AM',
            badge_status: 'Mastered',
            question_quote:
              'If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?',
            resolution_theorem: 'Karlin-Rubin Theorem',
          },
          {
            id: 'inq-2',
            topic: 'Causal DAGs',
            time: 'Oct 22, 16:40',
            badge_status: 'In Progress',
            question_quote:
              'Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?',
            resolution_theorem: 'Asymptotic bias vs variance distinction',
          },
          {
            id: 'inq-3',
            topic: 'LNP Formulation',
            time: 'Oct 20, 11:20',
            badge_status: 'Mastered',
            question_quote:
              'How does the mRNA lipid nanoparticle avoid early endosomal degradation?',
            resolution_theorem:
              'Ionizable lipids and pH-triggered endosomal escape',
          },
        ],
        upcoming_defense: {
          title: 'Neyman–Pearson LRT & Error Bounds',
          subtitle: 'Module 03 Capstone Validation',
          scheduled_time: 'Tomorrow at 10:00 AM',
          examiner_name: 'Dr. Julian Vance',
          examiner_role: 'Lead Examiner · Decision Theory',
          examiner_avatar:
            'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
          description:
            '45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.',
        },
        weekly_rhythm: [
          { day: 'Mon', height_pct: '60%', active: false },
          { day: 'Tue', height_pct: '45%', active: false },
          { day: 'Wed', height_pct: '85%', active: true },
          { day: 'Thu', height_pct: '70%', active: false },
          { day: 'Fri', height_pct: '95%', active: false },
          { day: 'Sat', height_pct: '30%', active: false },
          { day: 'Sun', height_pct: '50%', active: false },
        ],
      }
    ),

  uploadDocument: async (sessionId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const API_BASE =
      import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

    try {
      const res = await fetch(`${API_BASE}/intake/${sessionId}/document`, {
        method: 'POST',
        body: formData,
        headers: {
          'x-demo-mode': 'cached',
        },
      });
      if (!res.ok) {
        throw new Error(`Upload failed: ${res.statusText}`);
      }
      return (await res.json()) as DocumentUploadResponse;
    } catch (e) {
      console.warn('[Assay API] Upload fallback triggered:', e);
      return {
        session_id: sessionId,
        document_name: file.name,
        source_mode: 'document_rag',
        total_pages: 28,
        pages: [1, 2, 3, 4, 5],
        char_count: 14200,
        next: `/api/v1/intake/${sessionId}/checklist`,
        engine: 'deterministic_cache',
      } as DocumentUploadResponse;
    }
  },

  getSettings: () =>
    request<SettingsPayload>(
      '/settings',
      { method: 'GET' },
      {
        model: 'gemini-2.5-flash',
        rigor: 'academic',
        fallacy_sensitivity: 'balanced',
        audio_device: 'Default Microphone (High Definition Audio Device)',
      }
    ),

  updateSettings: (data: SettingsPayload) =>
    request<SettingsPayload>(
      '/settings',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      data
    ),
};

