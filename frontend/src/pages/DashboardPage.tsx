import React from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Avatar } from '../components/atoms/Avatar';
import {
  ArrowRight,
  BookOpen,
  Mic,
  Brain,
  Clock,
  ShieldCheck,
  ChevronRight,
  Compass,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { DashboardSummaryResponse } from '../types/api';
import { useAppStore } from '../store/useAppStore';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, setActiveChapterId } = useAppStore();
  const [data, setData] = React.useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setLoading(true);
    api.getDashboardSummary(activeSessionId)
      .then((res) => setData(res))
      .catch((err) => console.warn('Dashboard fetch error:', err))
      .finally(() => setLoading(false));
  }, [activeSessionId]);

  const d = data || {
    learner_name: 'Maya Lin',
    headline_subject: 'Causal Inference',
    remaining_modules: 2,
    active_subjects_count: 3,
    total_modules_count: 18,
    defenses_passed_count: 12,
    defenses_month_delta: '+3 this month',
    reasoning_depth_pct: 88,
    bloom_tier_label: 'First-Principles',
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
        question_quote: 'If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?',
        resolution_theorem: 'Karlin-Rubin Theorem',
      },
      {
        id: 'inq-2',
        topic: 'Causal DAGs',
        time: 'Oct 22, 16:40',
        badge_status: 'In Progress',
        question_quote: 'Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?',
        resolution_theorem: 'Asymptotic bias vs variance distinction',
      },
      {
        id: 'inq-3',
        topic: 'LNP Formulation',
        time: 'Oct 20, 11:20',
        badge_status: 'Mastered',
        question_quote: 'How does the mRNA lipid nanoparticle avoid early endosomal degradation?',
        resolution_theorem: 'Ionizable lipids and pH-triggered endosomal escape',
      },
    ],
    upcoming_defense: {
      title: 'Neyman–Pearson LRT & Error Bounds',
      subtitle: 'Module 03 Capstone Validation',
      scheduled_time: 'Tomorrow at 10:00 AM',
      examiner_name: 'Dr. Julian Vance',
      examiner_role: 'Lead Examiner · Decision Theory',
      examiner_avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
      description: '45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.',
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
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200 pb-12">
      {/* 1. Welcome Hero Card - Clean White Card with Right-Aligned Buttons (Figma 1:1886) */}
      <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-200/80 p-7 shadow-xs">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-indigo-600 tracking-wider uppercase font-mono">
              <span className="w-2 h-2 rounded-full bg-indigo-600" />
              OVERVIEW & DEFENSE PIPELINE
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Good morning, {d.learner_name}
            </h1>
            <p className="text-xs md:text-sm text-slate-500 leading-relaxed font-normal">
              You are {d.remaining_modules} modules away from completing <strong className="font-semibold text-slate-800">{d.headline_subject}</strong> and qualifying for your Capstone Oral Defense.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <Button
              variant="primary"
              size="md"
              className="bg-[#4338CA] hover:bg-[#3730A3] text-white font-bold px-5 py-2.5 rounded-full text-xs shadow-xs"
              onClick={() => navigate('/app/reader')}
              rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Resume Active Module
            </Button>
            <Button
              variant="outline"
              size="md"
              className="bg-[#EEF0FF] hover:bg-indigo-100 text-[#4338CA] border-transparent font-bold px-5 py-2.5 rounded-full text-xs transition-colors"
              onClick={() => navigate('/app/intake')}
            >
              Explore new topic
            </Button>
          </div>
        </div>

        {/* Decorative subtle backdrop curve */}
        <div className="absolute -right-16 -top-16 w-72 h-72 rounded-full bg-indigo-50/60 blur-2xl pointer-events-none" />
      </div>

      {/* 2. Four Key Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <Card className="p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider font-mono">
            <span>ACTIVE SUBJECTS</span>
            <BookOpen className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{d.active_subjects_count}</div>
            <div className="text-xs text-slate-400 font-medium">In progress across {d.total_modules_count} modules</div>
          </div>
        </Card>

        {/* Metric 2 */}
        <Card className="p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider font-mono">
            <span>ORAL DEFENSES PASSED</span>
            <span className="bg-emerald-50 text-emerald-700 text-[11px] font-semibold px-2 py-0.5 rounded-full">
              {d.defenses_month_delta}
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{d.defenses_passed_count}</div>
            <div className="text-xs text-slate-400 font-medium">Certified milestones</div>
          </div>
        </Card>

        {/* Metric 3 */}
        <Card className="p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider font-mono">
            <span>REASONING DEPTH</span>
            <span className="bg-indigo-50 text-indigo-700 text-[11px] font-semibold px-2 py-0.5 rounded-full">
              First-Principles
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">{d.reasoning_depth_pct}%</div>
            <div className="text-xs text-slate-400 font-medium">Bloom Level 5 (Synthesis)</div>
          </div>
        </Card>

        {/* Metric 4 */}
        <Card className="p-5 flex flex-col justify-between shadow-xs">
          <div className="flex items-center justify-between text-slate-400 text-xs font-bold uppercase tracking-wider font-mono">
            <span>WEEKLY FOCUS</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="my-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono flex items-baseline gap-1">
              {d.weekly_focus_hours}
              <span className="text-xs font-normal text-slate-400">hrs</span>
            </div>
            <div className="text-xs text-slate-400 font-medium">Active inquiry & defense</div>
          </div>
        </Card>
      </div>

      {/* 3. Main Grid: Left (Learning Paths & Inquiries) + Right (Upcoming Defense & Rhythm) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (8 Cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Section: In Progress Learning Paths */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-400 uppercase tracking-wider font-mono">
                CURRICULUM TRAJECTORY &bull; <strong className="text-slate-800 font-bold capitalize">In Progress Learning Paths</strong>
              </div>
              <button
                onClick={() => navigate('/app/roadmap')}
                className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
              >
                View all curricula <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Dynamic Learning Paths */}
            {(d.learning_paths || []).map((path) => {
              const activeCapsules = Math.max(1, Math.min(6, Math.round((path.progress_pct / 100) * 6)));
              const isRigorous = path.level_tag.toLowerCase().includes('rigorous');
              return (
                <Card
                  key={path.id}
                  hoverable
                  className="p-6 space-y-4 shadow-xs"
                  onClick={() => {
                    setActiveChapterId(path.id.startsWith('ch_') ? path.id : 'ch_01');
                    navigate(path.action_url || '/app/reader');
                  }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span
                          className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                            isRigorous
                              ? 'bg-amber-50 text-amber-800'
                              : 'bg-indigo-50 text-indigo-700'
                          }`}
                        >
                          {path.level_tag}
                        </span>
                        <span className="text-xs text-slate-400 font-medium">
                          {path.module_label}
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-slate-900 mt-1">
                        {path.title}
                      </h3>
                    </div>
                    <span className="text-xs text-slate-400 whitespace-nowrap font-medium">
                      {path.last_active}
                    </span>
                  </div>

                  {/* Segmented Progress Bar (6 Distinct Capsules) */}
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-1.5 w-full">
                      {[0, 1, 2, 3, 4, 5].map((idx) => (
                        <div
                          key={idx}
                          className={`h-2 rounded-full flex-1 transition-all ${
                            idx < activeCapsules ? 'bg-indigo-600' : 'bg-indigo-100'
                          }`}
                        />
                      ))}
                    </div>
                    <div className="flex items-center justify-between text-xs pt-0.5">
                      <span className="text-slate-500 font-medium">{path.concepts_defended}</span>
                      <span className="text-indigo-600 font-bold font-mono">
                        {path.progress_pct}% Phase Progress
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                    <div className="flex items-center gap-2 text-slate-700 font-medium">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          path.prerequisite_note.includes('unresolved')
                            ? 'bg-rose-500'
                            : 'bg-emerald-500'
                        }`}
                      />
                      <span>{path.prerequisite_note}</span>
                    </div>
                    <button
                      type="button"
                      className="bg-[#1E2238] hover:bg-[#151828] text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 transition-colors"
                    >
                      Continue dialogue &rarr;
                    </button>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Section: Recent Socratic Inquiries */}
          <div className="space-y-3 pt-2">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                DIALECTIC HISTORY
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Recent Socratic Inquiries
              </h2>
              <p className="text-xs text-slate-500">
                Probing questions explored during active reading and oral checks
              </p>
            </div>

            <div className="space-y-3">
              {(d.recent_inquiries || []).map((inq) => (
                <Card key={inq.id} className="p-5 space-y-3 shadow-xs">
                  <div className="flex items-center justify-between text-xs">
                    <span className="bg-indigo-50 text-indigo-700 text-[11px] font-semibold px-2 py-0.5 rounded-full">
                      {inq.topic}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400 font-mono text-[11px]">{inq.time}</span>
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                          inq.badge_status === 'Mastered'
                            ? 'bg-emerald-50 text-emerald-700'
                            : 'bg-amber-50 text-amber-700'
                        }`}
                      >
                        {inq.badge_status}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-800 font-medium leading-relaxed bg-slate-50/60 p-3 rounded-xl border border-slate-100">
                    &ldquo;{inq.question_quote}&rdquo;
                  </p>
                  <div className="flex items-center justify-between text-xs pt-1">
                    <span className="text-slate-500">
                      Resolution through <strong className="text-slate-700">{inq.resolution_theorem}</strong>
                    </span>
                    <button
                      onClick={() => navigate('/app/reader')}
                      className="text-indigo-600 font-semibold hover:underline flex items-center gap-1"
                    >
                      Revisit transcript <span className="text-[11px]">↗</span>
                    </button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (4 Cols): Upcoming Defense & Cognitive Rhythm & Rubric */}
        <div className="lg:col-span-4 space-y-6">
          {/* Upcoming Defense Card (Figma 1:1886) */}
          <Card className="p-6 border-slate-200/80 bg-white shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-600 tracking-wider font-mono">
                <Mic className="w-4 h-4 text-indigo-600" />
                <span>UPCOMING DEFENSE</span>
              </div>
              <span className="bg-amber-50 text-amber-800 border border-amber-200/60 text-[11px] font-semibold px-2.5 py-0.5 rounded-full">
                {d.upcoming_defense?.scheduled_time || 'Tomorrow at 10:00 AM'}
              </span>
            </div>

            <div>
              <h3 className="text-base font-extrabold text-slate-900 leading-snug">
                {d.upcoming_defense?.title || 'Neyman–Pearson LRT & Error Bounds'}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {d.upcoming_defense?.subtitle || 'Module 03 Capstone Validation'}
              </p>
            </div>

            {/* Dr. Julian Vance Examiner Card */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100 shadow-2xs">
              <Avatar name={d.upcoming_defense?.examiner_name || 'Julian Vance'} size="md" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold text-slate-900">
                  {d.upcoming_defense?.examiner_name || 'Dr. Julian Vance'}
                </div>
                <div className="text-[11px] text-slate-500">
                  {d.upcoming_defense?.examiner_role || 'Lead Examiner · Decision Theory'}
                </div>
              </div>
            </div>

            {/* Socratic inquiry box */}
            <div className="p-3 rounded-xl bg-indigo-50/50 border border-indigo-100 flex items-start gap-2.5 text-xs text-slate-600 leading-relaxed">
              <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
              <span>
                {d.upcoming_defense?.description || '45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.'}
              </span>
            </div>

            {/* Action button */}
            <button
              type="button"
              onClick={() => navigate('/app/exam')}
              className="w-full bg-[#EEF0FF] hover:bg-indigo-100 text-[#4338CA] font-bold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Review preparation notes</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </Card>

          {/* Weekly Inquiry Rhythm */}
          <Card className="p-6 space-y-3 shadow-xs">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                  COGNITIVE LOAD
                </span>
                <h3 className="text-sm font-bold text-slate-900">
                  Weekly Inquiry Rhythm
                </h3>
              </div>
              <span className="w-2 h-2 rounded-full bg-indigo-600" />
            </div>
            <p className="text-xs text-slate-500">
              Active dialogue & deep reading time
            </p>

            {/* 7-Day Rhythm Bar Chart (Figma 1:1886) */}
            <div className="h-28 flex items-end justify-between gap-2 pt-4 px-2">
              {(d.weekly_rhythm || []).map((item) => (
                <div key={item.day} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <div
                    className={`w-full rounded-t-md transition-all ${
                      item.active ? 'bg-indigo-600' : 'bg-indigo-100 hover:bg-indigo-200'
                    }`}
                    style={{ height: item.height_pct || '50%' }}
                  />
                  <span className={`text-[10px] font-mono ${item.active ? 'text-indigo-900 font-bold' : 'text-slate-400'}`}>
                    {item.day}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
              <span className="text-slate-500 font-medium">Daily avg: <strong className="text-slate-800">62 mins</strong></span>
              <span className="text-emerald-700 font-bold text-[11px] flex items-center gap-1">
                ↗ +37% vs target
              </span>
            </div>
          </Card>

          {/* Oral Defense Rubric Card (Figma 1:1886) */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs space-y-2">
            <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
              <Compass className="w-4 h-4 text-indigo-600" />
              <span>Oral Defense Rubric</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Your examiners grade based on Counter-factual Synthesis, Counter-example Construction, Boundary Precision, and Semantic Parsimony.
            </p>
            <a
              href="#rubric"
              onClick={(e) => {
                e.preventDefault();
                navigate('/app/exam');
              }}
              className="text-xs font-semibold text-indigo-600 hover:underline inline-flex items-center gap-1 pt-1"
            >
              View Socratic evaluation standards ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
