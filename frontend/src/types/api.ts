export type Role =
  | 'Frontend'
  | 'Backend'
  | 'Fullstack'
  | 'DevOps'
  | 'Data/ML'
  | 'Mobile'
  | 'QA/Test'
  | 'Security'
  | 'System Design'
  | string;

export interface RolesResponse {
  roles: string[];
  others_option: string;
}

export interface IntakeRequest {
  intent: string;
  role: string;
  role_is_custom?: boolean;
  custom_role?: string;
  document?: string | null;
}

export interface IntakeResponse {
  session_id: string;
  intent: string;
  role: string;
  has_document: boolean;
  available_roles: string[];
  suggested_others: boolean;
  next: string;
}

export type OriginType = 'document' | 'role_taxonomy' | 'grounded_external';

export interface ChecklistItem {
  item_id: string;
  topic: string;
  selected: boolean;
  confidence: number;
  origin: OriginType;
}

export interface ChecklistResponse {
  session_id: string;
  role: string;
  source: string;
  checklist: ChecklistItem[];
}

export type ChapterStatus =
  | 'LOCKED'
  | 'ACTIVE_READING'
  | 'INTERVIEW'
  | 'SCORED'
  | 'UNLOCKED'
  | 'NEEDS_REVIEW';

export interface ReferenceItem {
  kind: 'document' | 'grounded_external';
  label: string;
  page?: number;
  url?: string;
  verified?: boolean;
  cached?: boolean;
}

export interface ChapterMeta {
  chapter_id: string;
  title: string;
  order: number;
  status: ChapterStatus;
  prerequisites: string[];
  estimated_reading_minutes: number;
  source_pages: number[];
  references: ReferenceItem[];
}

export interface SyllabusResponse {
  session_id: string;
  syllabus_id: string;
  title: string;
  source_mode: 'document_rag' | 'role_taxonomy_generated';
  total_chapters: number;
  chapters: ChapterMeta[];
}

export interface ChapterDetailResponse {
  chapter_id: string;
  title: string;
  status: ChapterStatus;
  content_markdown: string;
  source_pages: number[];
  next_locked: boolean;
  interview_available: boolean;
}

export interface SocraticAskRequest {
  session_id: string;
  selected_text: string;
  question: string;
  anchor?: {
    page?: number;
    char_start?: number;
    char_end?: number;
  };
}

export interface SocraticAskResponse {
  mode: string;
  reply: string;
  hint_level: number;
  citations: Array<{ kind: string; page?: number }>;
  gave_direct_answer: boolean; // MUST be false
}

export interface SuggestionsResponse {
  selection: string;
  suggested_questions: string[];
}

export interface InterviewStartResponse {
  interview_id: string;
  chapter_id: string;
  turn_index: number;
  first_question: string;
  focus_mode: {
    required: boolean;
    available: boolean;
  };
}

export interface ClientTelemetry {
  paste_detected: boolean;
  duration_seconds: number;
  keystroke_cpm: number;
}

export interface InterviewTurnRequest {
  interview_id: string;
  turn_index: number;
  user_response: string;
  client_telemetry?: ClientTelemetry;
}

export interface HoneypotMetadata {
  injected_term: string;
  expected_action: string;
  source: string;
}

export interface InterviewTurnResponse {
  interview_id: string;
  turn_index: number;
  is_concluded: boolean;
  running_score: number;
  interrogator_response: string;
  honeypot_active: boolean;
  honeypot_metadata?: HoneypotMetadata;
}

export type HoneypotResult =
  | 'CRITICAL_REJECTION'
  | 'AI_HALLUCINATION_COPYPASTE'
  | 'UNVERIFIED_HONEST'
  | 'EVASIVE'
  | 'NONE';

export interface ScoreDetail {
  chapter_score: number;
  reasoning_score: number;
  integrity_score: number;
  honeypot_score: number;
}

export interface InterviewFinalizeResponse {
  interview_id: string;
  chapter_id: string;
  passed: boolean;
  score: ScoreDetail;
  honeypot_verdict: {
    term: string;
    result: HoneypotResult;
    analysis: string;
  };
  chapter_state_update: {
    current_chapter_status: ChapterStatus;
    next_unlocked_chapter_id?: string | null;
  };
  verifier: {
    status: string;
    note: string;
  };
}

export interface CalibrationResponse {
  predicted_score: number;
  actual_score: number;
  calibration_gap: number;
  label: 'well_calibrated' | 'overconfident' | 'underconfident';
}

export interface FocusEventItem {
  type: 'GAZE_DRIFT' | 'MULTIPLE_FACES' | 'TAB_BLUR' | 'CAMERA_OFF';
  at_ms: number;
  duration_ms?: number;
  count?: number;
}

export interface FocusEventsResponse {
  integrity_flag: string;
  auto_blur: boolean;
  summary: {
    gaze_drift_count: number;
    multi_face_count: number;
    tab_blur_count: number;
  };
}

export interface FinalReportResponse {
  session_id: string;
  syllabus_title: string;
  chapters: Array<{
    chapter_id: string;
    status: string;
    score: number;
    calibration_gap: number;
    integrity: string;
  }>;
  summary: {
    mean_score: number;
    mean_calibration_gap: number;
    integrity_flags: number;
    honeypot_verdicts: Record<string, number>;
  };
}

// Auth & Profile
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  handle: string;
  institution: string;
  streak_days: number;
  credits: number;
  avatar_url: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
  expires_in: number;
}

// Document Upload
export interface DocumentUploadResponse {
  session_id: string;
  document_name: string;
  source_mode: string;
  total_pages: number;
  pages: number[];
  char_count: number;
  next: string;
  engine: string;
}

// Dashboard Summary
export interface LearningPathSummary {
  id: string;
  title: string;
  level_tag: string;
  module_label: string;
  last_active: string;
  concepts_defended: string;
  progress_pct: number;
  prerequisite_note: string;
  action_url: string;
}

export interface SocraticInquiryRecord {
  id: string;
  topic: string;
  time: string;
  badge_status: string;
  question_quote: string;
  resolution_theorem: string;
}

export interface UpcomingDefenseInfo {
  title: string;
  subtitle: string;
  scheduled_time: string;
  examiner_name: string;
  examiner_role: string;
  examiner_avatar: string;
  description: string;
}

export interface DayRhythm {
  day: string;
  height_pct: string;
  active: boolean;
}

export interface DashboardSummaryResponse {
  learner_name: string;
  headline_subject: string;
  remaining_modules: number;
  active_subjects_count: number;
  total_modules_count: number;
  defenses_passed_count: number;
  defenses_month_delta: string;
  reasoning_depth_pct: number;
  bloom_tier_label: string;
  weekly_focus_hours: number;
  learning_paths: LearningPathSummary[];
  recent_inquiries: SocraticInquiryRecord[];
  upcoming_defense: UpcomingDefenseInfo;
  weekly_rhythm: DayRhythm[];
}

// Settings
export interface SettingsPayload {
  model: string;
  rigor: string;
  fallacy_sensitivity: string;
  audio_device?: string;
}
