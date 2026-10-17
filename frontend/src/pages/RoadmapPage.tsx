import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import {
  CheckCircle2,
  Clock,
  BookOpen,
  Mic,
  ArrowRight,
  Lock,
  Sparkles,
  ChevronRight,
  TrendingUp,
  FileCheck,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { api } from '../services/api';
import { SyllabusResponse } from '../types/api';

export const RoadmapPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, setActiveChapterId } = useAppStore();
  const [activeTab, setActiveTab] = useState<'roadmap' | 'prerequisites' | 'schedule'>('roadmap');
  const [syllabus, setSyllabus] = useState<SyllabusResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sid = activeSessionId || 'sess_coding_basic';
    api.getSyllabus(sid)
      .then((res) => setSyllabus(res))
      .catch((err) => console.warn('Roadmap syllabus fetch fallback:', err))
      .finally(() => setLoading(false));
  }, [activeSessionId]);

  const fallbackModules = [
    {
      id: 'mod-1',
      number: '01',
      title: 'Probability Axioms & Joint Distributions',
      status: 'completed' as const,
      statusLabel: 'MODULE 01 · COMPLETED',
      time: '2.0h completed',
      description:
        'Establish foundational probability spaces, independence properties, and Bayes theorem under uncertainty.',
      conceptsCount: '4 concepts',
      badge: 'Passed Oral Defense',
      score: '96%',
    },
    {
      id: 'mod-2',
      number: '02',
      title: 'Maximum Likelihood & Point Estimation',
      status: 'in_progress' as const,
      statusLabel: 'MODULE 02 · IN PROGRESS',
      time: '1.5h of 2.5h',
      description:
        'Derive likelihood equations, score functions, and asymptotic normality under adversarial inquiry.',
      conceptsCount: '5 concepts',
      badge: 'Oral defense scheduled',
      actionLabel: 'Resume dialogue',
    },
    {
      id: 'mod-3',
      number: '03',
      title: 'Neyman–Pearson Lemma & Likelihood Ratio Tests',
      status: 'ready' as const,
      statusLabel: 'MODULE 03 · READY TO READ',
      time: '2.5h estimated',
      description:
        'Formulate uniformly most powerful tests, false discovery rates, and trade-offs between Type I and Type II errors.',
      conceptsCount: '6 concepts',
      badge: 'Next in sequence',
      actionLabel: 'Start reading',
    },
    {
      id: 'mod-4',
      number: '04',
      title: 'Confidence Intervals & Duality with Hypothesis Testing',
      status: 'locked' as const,
      statusLabel: 'MODULE 04 · LOCKED',
      time: '2.0h',
      description:
        'Connect confidence sets with inverted acceptance regions and pivot methods.',
      conceptsCount: '4 concepts',
      prereq: 'Prerequisite: Pass Module 03 Oral Defense',
    },
    {
      id: 'mod-5',
      number: '05',
      title: 'Bayesian Inference & Conjugate Priors',
      status: 'locked' as const,
      statusLabel: 'MODULE 05 · LOCKED',
      time: '2.5h',
      description:
        'Posterior distributions, loss functions, and admissible estimators in decision theory.',
      conceptsCount: '5 concepts',
      prereq: 'Prerequisite: Pass Module 04',
    },
    {
      id: 'mod-6',
      number: '06',
      title: 'Capstone Oral Defense: Socratic Grand Jury',
      status: 'locked' as const,
      statusLabel: 'MODULE 06 · CAPSTONE',
      time: '2.5h',
      description:
        'Comprehensive 45-min live vocal defense covering all 6 statistical decision modules.',
      conceptsCount: '6 competencies',
      prereq: 'Prerequisite: Pass all prior 5 modules',
    },
  ];

  const modules = (syllabus?.chapters && syllabus.chapters.length > 0)
    ? syllabus.chapters.map((ch, idx) => {
        const numStr = String(ch.order || idx + 1).padStart(2, '0');
        const st = (ch.status || 'LOCKED').toUpperCase();
        const isCompleted = st === 'COMPLETED' || st === 'SCORED' || st === 'UNLOCKED';
        const isInProgress = st === 'ACTIVE_READING' || st === 'INTERVIEW';
        const isReady = st === 'READY' || (idx === 1 && !isInProgress && !isCompleted);
        const isLocked = !isCompleted && !isInProgress && !isReady;

        const statusType: 'completed' | 'in_progress' | 'ready' | 'locked' =
          isCompleted ? 'completed' : (isInProgress ? 'in_progress' : (isReady ? 'ready' : 'locked'));

        let statusLabel = `MODULE ${numStr} · ${st.replace('_', ' ')}`;
        if (isCompleted) statusLabel = `MODULE ${numStr} · COMPLETED`;
        else if (isInProgress) statusLabel = `MODULE ${numStr} · IN PROGRESS`;
        else if (isReady) statusLabel = `MODULE ${numStr} · READY TO READ`;
        else statusLabel = `MODULE ${numStr} · LOCKED`;

        return {
          id: ch.chapter_id,
          number: numStr,
          title: ch.title,
          status: statusType,
          statusLabel,
          time: `${ch.estimated_reading_minutes || 20}m`,
          description: ch.prerequisites?.length
            ? `Prerequisites: ${ch.prerequisites.join(', ')}`
            : `Socratic inquiry module covering fundamental proofs, bounds, and adversarial counter-arguments.`,
          conceptsCount: `${(ch.source_pages || []).length ? (ch.source_pages || []).length + 3 : 4} concepts`,
          badge: isCompleted
            ? 'Passed Oral Defense'
            : (isInProgress ? 'Oral defense scheduled' : (isReady ? 'Next in sequence' : 'Locked')),
          score: isCompleted ? '96%' : undefined,
          actionLabel: isInProgress ? 'Resume dialogue' : (isReady ? 'Start reading' : undefined),
          prereq: ch.prerequisites?.length ? `Prerequisite: Pass ${ch.prerequisites[0]}` : undefined,
        };
      })
    : fallbackModules;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-200 pb-12">
      {/* Breadcrumb & Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400">
          <span>SUBJECTS</span>
          <span>/</span>
          <span className="text-primary-600 font-bold uppercase truncate max-w-xs">
            {syllabus?.title || (activeSessionId === 'sess_coding_basic' ? 'FOUNDATIONS OF ALGORITHMS & DATA STRUCTURES' : 'STATISTICAL DECISION THEORY')}
          </span>
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
          Curated Learning Roadmap: {syllabus?.title || (activeSessionId === 'sess_coding_basic' ? 'Foundations of Algorithms & Data Structures' : 'Statistical Decision Theory')}
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          A verified sequence of {modules.length} inquiry modules designed for Socratic oral defense and first-principles mastery.
        </p>
      </div>

      {/* Tabs & Metrics Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-2">
          {(['roadmap', 'prerequisites', 'schedule'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`capitalize px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                activeTab === tab
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-6 text-xs">
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Total Modules</div>
            <div className="font-extrabold text-slate-900 font-mono text-base">{modules.length}</div>
          </div>
          <div className="w-px h-6 bg-slate-200" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Estimated Inquiry</div>
            <div className="font-extrabold text-slate-900 font-mono text-base">
              {(modules.length * 2.2).toFixed(1)} hrs
            </div>
          </div>
          <div className="w-px h-6 bg-slate-200" />
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase">Readiness Score</div>
            <div className="font-extrabold text-primary-600 font-mono text-base">72%</div>
          </div>
        </div>
      </div>

      {/* Roadmap Timeline List */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-200">
        {modules.map((mod) => {
          const isCompleted = mod.status === 'completed';
          const isInProgress = mod.status === 'in_progress';
          const isReady = mod.status === 'ready';
          const isLocked = mod.status === 'locked';

          return (
            <div key={mod.id} className="relative group">
              {/* Stepper Dot on the Timeline Line */}
              <div
                className={`absolute -left-[31px] top-4 w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold transition-transform group-hover:scale-110 ${
                  isCompleted
                    ? 'bg-emerald-500 border-white text-white shadow-xs'
                    : isInProgress
                    ? 'bg-primary-600 border-white text-white ring-4 ring-primary-100 shadow-sm'
                    : isReady
                    ? 'bg-white border-primary-500 text-primary-600'
                    : 'bg-slate-100 border-slate-300 text-slate-400'
                }`}
              >
                {isCompleted ? '✓' : mod.number}
              </div>

              {/* Module Card */}
              <Card
                className={`p-5 transition-all ${
                  isInProgress
                    ? 'border-primary-300 bg-white shadow-hover ring-1 ring-primary-100'
                    : isLocked
                    ? 'bg-slate-50/70 border-slate-200 opacity-70'
                    : 'bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-[11px] font-bold tracking-wider font-mono ${
                          isCompleted
                            ? 'text-emerald-700'
                            : isInProgress
                            ? 'text-primary-600'
                            : 'text-slate-400'
                        }`}
                      >
                        {mod.statusLabel}
                      </span>
                      <span className="text-slate-300">&bull;</span>
                      <span className="text-xs text-slate-400 font-mono">{mod.time}</span>
                    </div>
                    <h3 className="text-base font-bold text-slate-900">
                      {mod.title}
                    </h3>
                  </div>

                  {/* Top Right Badges */}
                  <div>
                    {isCompleted && (
                      <Badge variant="success" size="sm">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                        {mod.badge}
                      </Badge>
                    )}
                    {isInProgress && (
                      <Badge variant="primary" size="sm" hasDot>
                        {mod.badge}
                      </Badge>
                    )}
                    {isLocked && (
                      <Badge variant="slate" size="sm">
                        <Lock className="w-3 h-3 mr-1" />
                        Locked
                      </Badge>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  {mod.description}
                </p>

                {/* Footer Controls */}
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
                  <div className="flex items-center gap-3 text-slate-400 font-medium">
                    <span className="flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5" />
                      {mod.conceptsCount}
                    </span>
                    {mod.prereq && (
                      <span className="text-slate-400 text-[11px] italic">
                        {mod.prereq}
                      </span>
                    )}
                  </div>

                  <div>
                    {isCompleted && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate('/app/report')}
                        className="text-emerald-700 hover:bg-emerald-50 text-xs font-semibold"
                      >
                        View Defense Dossier ({mod.score}) &rarr;
                      </Button>
                    )}
                    {isInProgress && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => {
                          setActiveChapterId(mod.id);
                          navigate('/app/reader');
                        }}
                        rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                      >
                        {mod.actionLabel}
                      </Button>
                    )}
                    {isReady && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setActiveChapterId(mod.id);
                          navigate('/app/reader');
                        }}
                        rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                      >
                        {mod.actionLabel}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            </div>
          );
        })}
      </div>
    </div>
  );
};
