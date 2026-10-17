import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import {
  Check,
  Clock,
  ArrowRight,
  Lock,
  Sparkles,
  Calendar,
  Layers,
  PieChart,
  BookOpen,
  FileText,
  ShieldCheck,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { api } from '../services/api';
import { SyllabusResponse } from '../types/api';

export const RoadmapPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, setActiveChapterId, user } = useAppStore();
  const [activeTab, setActiveTab] = useState<'roadmap' | 'prerequisites' | 'schedule'>('roadmap');
  const [syllabus, setSyllabus] = useState<SyllabusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const learnerName = user?.name ? user.name.split(' ')[0] : 'Rafida';

  useEffect(() => {
    const sid = activeSessionId || 'sess_math_stats';
    api.getSyllabus(sid)
      .then((res) => setSyllabus(res))
      .catch((err) => console.warn('Roadmap syllabus fetch fallback:', err))
      .finally(() => setLoading(false));
  }, [activeSessionId]);

  // Curriculum definition matching Figma 1:704 exactly for Statistics for Decisions
  const getFigmaStatsModules = () => [
    {
      id: 'ch_01',
      number: '01',
      title: 'Probability Axioms & Joint Distributions',
      status: 'completed' as const,
      statusPill: 'MODULE 01 · COMPLETED',
      time: '2.0h completed',
      description: 'Establish foundational probability spaces, independence properties, and Bayes theorem under uncertainty.',
      segmentsFilled: 5,
      totalSegments: 5,
      conceptsCount: '4 concepts',
      badge: 'Passed Oral Defense',
      badgeVariant: 'success' as const,
    },
    {
      id: 'ch_02',
      number: '02',
      title: 'Maximum Likelihood & Point Estimation',
      status: 'in_progress' as const,
      statusPill: 'MODULE 02 · IN PROGRESS',
      time: '1.5h of 2.5h',
      description: 'Derive likelihood equations, score functions, and asymptotic normality under adversarial inquiry.',
      segmentsFilled: 3,
      totalSegments: 5,
      conceptsCount: '5 concepts',
      badge: 'Oral defense scheduled',
      badgeVariant: 'warning' as const,
      actionLabel: 'Resume dialogue',
    },
    {
      id: 'ch_03',
      number: '03',
      title: 'Hypothesis Testing & Neyman–Pearson Lemma',
      status: 'ready' as const,
      statusPill: 'MODULE 03',
      time: '2.5h',
      description: 'Uniformly most powerful tests, likelihood ratio tests, and Type I/II trade-offs in clinical trials.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '6 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
      actionLabel: 'Start reading',
    },
    {
      id: 'ch_04',
      number: '04',
      title: 'Bayesian Inference & Conjugate Priors',
      status: 'locked' as const,
      statusPill: 'MODULE 04',
      time: '2.5h',
      description: 'Posterior updating, Markov Chain Monte Carlo intuitions, and credible vs confidence intervals.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '5 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
    },
    {
      id: 'ch_05',
      number: '05',
      title: 'Causal Inference & Potential Outcomes',
      status: 'locked' as const,
      statusPill: 'MODULE 05',
      time: '2.5h',
      description: 'Confounding bias, backdoor criteria, propensity scoring, and instrumental variables.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '4 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
    },
    {
      id: 'ch_06',
      number: '06',
      title: 'Adversarial Socratic Defense: Synthesis',
      status: 'locked' as const,
      statusPill: 'MODULE 06 · CAPSTONE',
      time: '2.0h',
      description: 'Comprehensive 45-minute multi-domain oral examination against rigorous counter-evidence.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: 'Synthesis',
      badge: 'Rigorous Capstone',
      badgeVariant: 'capstone' as const,
    },
  ];

  // Coding track modules fallback
  const getCodingModules = () => [
    {
      id: 'ch_algo_01',
      number: '01',
      title: 'Asymptotic Notation & Algorithmic Complexity (O, Ω, Θ)',
      status: 'completed' as const,
      statusPill: 'MODULE 01 · COMPLETED',
      time: '2.0h completed',
      description: 'Establish foundational growth frontiers, worst-case invariants, and master theorem asymptotic bounds.',
      segmentsFilled: 5,
      totalSegments: 5,
      conceptsCount: '4 concepts',
      badge: 'Passed Oral Defense',
      badgeVariant: 'success' as const,
    },
    {
      id: 'ch_algo_02',
      number: '02',
      title: 'Linear Data Structures: Vectors, Ring Buffers & Memory Layout',
      status: 'in_progress' as const,
      statusPill: 'MODULE 02 · IN PROGRESS',
      time: '1.5h of 2.5h',
      description: 'Amortized geometric doubling, memory cache locality, and zero-copy circular ring buffer boundaries.',
      segmentsFilled: 3,
      totalSegments: 5,
      conceptsCount: '5 concepts',
      badge: 'Oral defense scheduled',
      badgeVariant: 'warning' as const,
      actionLabel: 'Resume dialogue',
    },
    {
      id: 'ch_algo_03',
      number: '03',
      title: 'Divide & Conquer: Quicksort, Mergesort & Recurrence Master Theorem',
      status: 'ready' as const,
      statusPill: 'MODULE 03',
      time: '2.5h',
      description: 'Partitioning invariants, adversarial worst-case inputs, and median-of-three pivot defense.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '6 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
      actionLabel: 'Start reading',
    },
    {
      id: 'ch_algo_04',
      number: '04',
      title: 'Nonlinear Structures: Balanced BSTs, AVL & Red-Black Invariants',
      status: 'locked' as const,
      statusPill: 'MODULE 04',
      time: '2.5h',
      description: 'Tree rotations, strict height invariants, and logarithmic lookup guarantees under adversarial insertion.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '5 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
    },
    {
      id: 'ch_algo_05',
      number: '05',
      title: 'Graph Theory: Breadth-First, Depth-First & Shortest Paths',
      status: 'locked' as const,
      statusPill: 'MODULE 05',
      time: '2.5h',
      description: 'Topological sort, cycle detection, Dijkstra greedy relaxation, and Bellman-Ford negative edge bounds.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: '6 concepts',
      badge: 'Oral defense',
      badgeVariant: 'neutral' as const,
    },
    {
      id: 'ch_algo_06',
      number: '06',
      title: 'Dynamic Programming: Optimal Substructure & Capstone Defense',
      status: 'locked' as const,
      statusPill: 'MODULE 06 · CAPSTONE',
      time: '2.0h',
      description: 'Overlapping subproblems, state space DAG traversal, and knapsack transition function defense.',
      segmentsFilled: 0,
      totalSegments: 5,
      conceptsCount: 'Synthesis',
      badge: 'Rigorous Capstone',
      badgeVariant: 'capstone' as const,
    },
  ];

  // Dynamic modules computation
  const isCodingSession = activeSessionId === 'sess_coding_basic';
  const modules = (() => {
    if (syllabus?.chapters && syllabus.chapters.length > 0) {
      return syllabus.chapters.map((ch, idx) => {
        const numStr = String(ch.order || idx + 1).padStart(2, '0');
        const st = (ch.status || 'LOCKED').toUpperCase();
        const isCompleted = st === 'COMPLETED' || st === 'SCORED' || st === 'UNLOCKED';
        const isInProgress = st === 'ACTIVE_READING' || st === 'INTERVIEW' || (idx === 1 && !isCompleted);
        const isReady = st === 'READY' || (idx === 2 && !isInProgress && !isCompleted);
        const isCapstone = idx === syllabus.chapters.length - 1;

        let statusPill = `MODULE ${numStr}`;
        if (isCompleted) statusPill = `MODULE ${numStr} · COMPLETED`;
        else if (isInProgress) statusPill = `MODULE ${numStr} · IN PROGRESS`;
        else if (isCapstone) statusPill = `MODULE ${numStr} · CAPSTONE`;

        let timeStr = `${((ch.estimated_reading_minutes || 30) / 15 * 0.5).toFixed(1)}h`;
        if (isCompleted) timeStr = '2.0h completed';
        else if (isInProgress) timeStr = '1.5h of 2.5h';

        return {
          id: ch.chapter_id,
          number: numStr,
          title: ch.title,
          status: isCompleted ? ('completed' as const) : (isInProgress ? ('in_progress' as const) : (isReady ? ('ready' as const) : ('locked' as const))),
          statusPill,
          time: timeStr,
          description: ch.prerequisites?.length
            ? `Prerequisites: ${ch.prerequisites.join(', ')}. Socratic inquiry module covering fundamental proofs, bounds, and adversarial counter-arguments.`
            : `Socratic inquiry module covering fundamental proofs, bounds, and adversarial counter-arguments.`,
          segmentsFilled: isCompleted ? 5 : (isInProgress ? 3 : 0),
          totalSegments: 5,
          conceptsCount: isCapstone ? 'Synthesis' : `${ch.source_pages?.length ? ch.source_pages.length + 3 : 4 + (idx % 3)} concepts`,
          badge: isCompleted ? 'Passed Oral Defense' : (isInProgress ? 'Oral defense scheduled' : (isCapstone ? 'Rigorous Capstone' : 'Oral defense')),
          badgeVariant: isCompleted ? ('success' as const) : (isInProgress ? ('warning' as const) : (isCapstone ? ('capstone' as const) : ('neutral' as const))),
          actionLabel: isInProgress ? 'Resume dialogue' : (isReady ? 'Start reading' : undefined),
        };
      });
    }

    return isCodingSession ? getCodingModules() : getFigmaStatsModules();
  })();

  const activeModule = modules.find((m) => m.status === 'in_progress') || modules[1] || modules[0];
  const activeChapterId = activeModule.id;
  const activeChapterNumber = activeModule.number;

  const subjectTitle = syllabus?.title || (isCodingSession ? 'Algorithms & Data Structures' : 'Statistics for Decisions');
  const breadcrumbTrack = isCodingSession ? 'COMPUTER SCIENCE' : 'STATISTICS FOR DECISIONS';

  return (
    <div className="max-w-[1240px] mx-auto space-y-7 animate-in fade-in duration-200 pb-16 font-sans">
      {/* Top Header Section with Right-Aligned Pills */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pt-2">
        <div className="space-y-1.5 max-w-3xl">
          {/* Breadcrumb */}
          <div className="flex items-center gap-1.5 text-xs font-bold tracking-wider text-slate-400 uppercase">
            <span>SUBJECTS</span>
            <span className="text-slate-300">/</span>
            <span className="text-slate-900">{breadcrumbTrack}</span>
          </div>

          {/* Heading */}
          <h1 className="text-2xl md:text-3xl font-extrabold text-[#0F172A] tracking-tight">
            Curated Learning Roadmap: {subjectTitle}
          </h1>

          {/* Subtitle */}
          <p className="text-sm text-slate-500 leading-relaxed">
            A verified sequence of {modules.length} inquiry modules designed for Socratic oral defense and first-principles mastery.
          </p>
        </div>

        {/* Tab Pills (Figma 1:704 Top Right) */}
        <div className="shrink-0 bg-slate-100 p-1 rounded-full inline-flex items-center self-start">
          <button
            onClick={() => setActiveTab('roadmap')}
            className={`px-5 py-2 rounded-full text-xs font-bold transition-all ${
              activeTab === 'roadmap'
                ? 'bg-[#0F172A] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Roadmap
          </button>
          <button
            onClick={() => setActiveTab('prerequisites')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'prerequisites'
                ? 'bg-[#0F172A] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Prerequisites
          </button>
          <button
            onClick={() => setActiveTab('schedule')}
            className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
              activeTab === 'schedule'
                ? 'bg-[#0F172A] text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Schedule
          </button>
        </div>
      </div>

      {/* 3 Metric Cards Row (Figma 1:704) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Metric 1: Total Modules */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-[11px] font-bold tracking-wider uppercase">TOTAL MODULES</span>
            <FileText className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 font-mono">{modules.length}</span>
            <span className="text-xs text-slate-400 font-medium">Foundational to Applied</span>
          </div>
        </div>

        {/* Metric 2: Estimated Inquiry */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-[11px] font-bold tracking-wider uppercase">ESTIMATED INQUIRY</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 font-mono">14.0 hrs</span>
            <span className="text-xs text-slate-400 font-medium">Self-paced pacing</span>
          </div>
        </div>

        {/* Metric 3: Readiness Score */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400">READINESS SCORE</span>
            <span className="bg-emerald-50 text-emerald-600 border border-emerald-100/60 rounded-full px-2 py-0.5 text-[11px] font-bold font-mono">
              +8% vs cohort
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-black text-slate-900 font-mono">72%</span>
            <span className="text-xs text-slate-400 font-medium">Optimal baseline</span>
          </div>
        </div>
      </div>

      {/* Main 2-Column Content Layout (Figma 1:704) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Vertical Timeline & Module Cards (8 cols) */}
        <div className="lg:col-span-8">
          <div className="relative pl-12 space-y-6 before:absolute before:left-5 before:top-6 before:bottom-6 before:w-[2px] before:bg-slate-200">
            {modules.map((mod) => {
              const isCompleted = mod.status === 'completed';
              const isInProgress = mod.status === 'in_progress';
              const isReady = mod.status === 'ready';
              const isLocked = mod.status === 'locked';

              return (
                <div key={mod.id} className="relative group">
                  {/* Timeline Stepper Dot / Circle on the Left */}
                  <div
                    className={`absolute -left-12 top-5 w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                      isCompleted
                        ? 'bg-emerald-100 text-emerald-700 shadow-xs'
                        : isInProgress
                        ? 'bg-[#4338CA] text-white ring-4 ring-indigo-100 shadow-md'
                        : 'bg-white border border-slate-200 text-slate-400'
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5 stroke-[2.5]" />
                    ) : (
                      <span className="text-xs font-black font-mono">{mod.number}</span>
                    )}
                  </div>

                  {/* Module Card */}
                  <div
                    className={`bg-white rounded-2xl border p-6 transition-all ${
                      isInProgress
                        ? 'border-indigo-200 shadow-sm ring-1 ring-indigo-50'
                        : 'border-slate-100 shadow-xs hover:border-slate-200'
                    }`}
                  >
                    {/* Top Pill & Time Row */}
                    <div className="flex items-center justify-between gap-3 mb-2.5">
                      <div>
                        {isCompleted && (
                          <span className="bg-emerald-50 text-emerald-700 border border-emerald-100 rounded-full px-3 py-1 text-[11px] font-bold font-mono tracking-wider">
                            {mod.statusPill}
                          </span>
                        )}
                        {isInProgress && (
                          <span className="bg-[#4338CA] text-white rounded-full px-3 py-1 text-[11px] font-bold font-mono tracking-wider shadow-xs">
                            {mod.statusPill}
                          </span>
                        )}
                        {!isCompleted && !isInProgress && mod.badgeVariant === 'capstone' && (
                          <span className="bg-rose-50 text-rose-600 border border-rose-100 rounded-full px-3 py-1 text-[11px] font-bold font-mono tracking-wider">
                            {mod.statusPill}
                          </span>
                        )}
                        {!isCompleted && !isInProgress && mod.badgeVariant !== 'capstone' && (
                          <span className="bg-slate-100 text-slate-600 rounded-full px-3 py-1 text-[11px] font-bold font-mono tracking-wider">
                            {mod.statusPill}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{mod.time}</span>
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="text-base md:text-lg font-bold text-slate-900 tracking-tight mb-1.5">
                      {mod.title}
                    </h3>

                    {/* Description */}
                    <p className="text-xs text-slate-500 leading-relaxed mb-4">
                      {mod.description}
                    </p>

                    {/* Segmented Progress Bar (5 Segments - Figma 1:704) */}
                    <div className="grid grid-cols-5 gap-1.5 my-3.5">
                      {Array.from({ length: mod.totalSegments }).map((_, segIdx) => {
                        const isFilled = segIdx < mod.segmentsFilled;
                        let segClass = 'bg-slate-100';
                        if (isFilled) {
                          segClass = isCompleted ? 'bg-emerald-600' : 'bg-indigo-600';
                        }
                        return (
                          <div
                            key={segIdx}
                            className={`h-1.5 rounded-full transition-all ${segClass}`}
                          />
                        );
                      })}
                    </div>

                    {/* Footer Badges & Actions */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        {/* Concepts count pill */}
                        <span className="inline-flex items-center gap-1.5 bg-white border border-slate-200 text-slate-600 text-xs font-medium px-2.5 py-1 rounded-full">
                          <Layers className="w-3.5 h-3.5 text-slate-400" />
                          <span>{mod.conceptsCount}</span>
                        </span>

                        {/* Status / Defense badge */}
                        {mod.badgeVariant === 'success' && (
                          <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-emerald-100/60">
                            <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                            <span>{mod.badge}</span>
                          </span>
                        )}

                        {mod.badgeVariant === 'warning' && (
                          <span className="inline-flex items-center gap-1.5 bg-amber-50 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-amber-100/60">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
                            <span>{mod.badge}</span>
                          </span>
                        )}

                        {mod.badgeVariant === 'capstone' && (
                          <span className="inline-flex items-center gap-1.5 bg-rose-50 text-rose-600 text-xs font-semibold px-2.5 py-1 rounded-full border border-rose-100/60">
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>{mod.badge}</span>
                          </span>
                        )}

                        {mod.badgeVariant === 'neutral' && (
                          <span className="inline-flex items-center gap-1.5 bg-slate-50 text-slate-600 border border-slate-200 text-xs font-medium px-2.5 py-1 rounded-full">
                            <ArrowRight className="w-3.5 h-3.5 text-slate-400 rotate-90" />
                            <span>{mod.badge}</span>
                          </span>
                        )}
                      </div>

                      {/* Right Action Trigger */}
                      {isInProgress && (
                        <button
                          onClick={() => {
                            setActiveChapterId(mod.id);
                            navigate('/app/reader');
                          }}
                          className="inline-flex items-center gap-1.5 text-indigo-600 hover:text-indigo-800 text-xs font-bold transition-colors cursor-pointer group-hover:underline"
                        >
                          <span>{mod.actionLabel || 'Resume dialogue'}</span>
                          <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                        </button>
                      )}

                      {isReady && (
                        <button
                          onClick={() => {
                            setActiveChapterId(mod.id);
                            navigate('/app/reader');
                          }}
                          className="inline-flex items-center gap-1.5 text-slate-600 hover:text-slate-900 text-xs font-semibold transition-colors cursor-pointer"
                        >
                          <span>{mod.actionLabel || 'Start reading'}</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: 3 Auxiliary Cards (4 cols - Figma 1:704) */}
        <div className="lg:col-span-4 space-y-5 sticky top-6">
          {/* Card 1: Active Stage / Defense Card */}
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-3.5">
              {/* Circular Gauge Ring (38%) */}
              <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
                <svg className="w-12 h-12 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-slate-100"
                    strokeWidth="3.5"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="text-[#4338CA]"
                    strokeDasharray="38, 100"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <span className="absolute text-xs font-black font-mono text-slate-900">38%</span>
              </div>

              <div>
                <div className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                  ACTIVE STAGE
                </div>
                <h3 className="text-sm font-bold text-slate-900 leading-snug">
                  Ready to defend Module {activeChapterNumber}?
                </h3>
              </div>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed">
              {learnerName}, your next checkpoint covers Score Functions and Fisher Information Matrix with the Socratic dialogue evaluator.
            </p>

            <button
              onClick={() => {
                setActiveChapterId(activeChapterId);
                navigate('/app/reader');
              }}
              className="w-full bg-[#0F172A] hover:bg-[#1E293B] text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 text-xs shadow-xs transition-all cursor-pointer"
            >
              <span>Resume Module {parseInt(activeChapterNumber, 10)}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={() => navigate('/app/intake')}
              className="text-xs text-slate-400 hover:text-slate-600 text-center w-full block cursor-pointer font-medium pt-0.5"
            >
              Adjust path & pacing
            </button>
          </div>

          {/* Card 2: Subject Prerequisites Card */}
          <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-xs space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Subject Prerequisites</h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Verified baseline readiness before Socratic probing.
              </p>
            </div>

            <div className="space-y-2.5">
              {/* Item 1 */}
              <div className="bg-[#F8FAFC] border border-slate-100 rounded-xl p-3 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-800">
                  {isCodingSession ? 'Discrete Mathematics & Logic' : 'Multivariable Calculus'}
                </span>
                <span className="bg-emerald-50 text-emerald-600 text-[11px] font-bold px-2.5 py-0.5 rounded-md font-mono">
                  Ready
                </span>
              </div>

              {/* Item 2 */}
              <div className="bg-[#F8FAFC] border border-slate-100 rounded-xl p-3 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-800">
                  {isCodingSession ? 'Basic Asymptotic Complexity' : 'Linear Algebra & Spectral Decomp'}
                </span>
                <span className="bg-emerald-50 text-emerald-600 text-[11px] font-bold px-2.5 py-0.5 rounded-md font-mono">
                  Ready
                </span>
              </div>

              {/* Item 3 */}
              <div className="bg-[#F8FAFC] border border-slate-100 rounded-xl p-3 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-800">
                    {isCodingSession ? 'Pointer & Memory Models' : 'Real Analysis & Convergence'}
                  </span>
                  <span className="bg-amber-50 text-amber-700 text-[11px] font-bold px-2.5 py-0.5 rounded-md font-mono">
                    Review
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">Optional brush-up available</span>
              </div>
            </div>
          </div>

          {/* Card 3: Oral Defense Checkpoint Card */}
          <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-xs">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-[10px] font-bold tracking-wider uppercase">
                ORAL DEFENSE CHECKPOINT
              </span>
              <Calendar className="w-4 h-4 text-slate-400" />
            </div>

            <div className="flex items-center justify-between mt-2 mb-1">
              <span className="text-base font-black text-slate-900 font-mono tracking-tight">
                Oct 24, 14:00
              </span>
              <span className="bg-indigo-50 text-indigo-600 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                Voice Direct
              </span>
            </div>

            <p className="text-xs text-slate-400 font-medium">
              Est. duration: 30 mins
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
