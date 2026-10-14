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
  FinalReportResponse
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

async function request<T>(endpoint: string, options?: RequestInit, mockFallback?: T): Promise<T> {
  if (USE_MOCK && mockFallback !== undefined) {
    return Promise.resolve(mockFallback);
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'x-demo-mode': 'cached',
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
    )
};
