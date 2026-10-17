import React from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Avatar } from '../components/atoms/Avatar';
import {
  Sparkles,
  ArrowRight,
  BookOpen,
  Mic,
  Brain,
  Clock,
  CheckCircle2,
  Calendar,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  BarChart3,
  Flame,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { DashboardSummaryResponse } from '../types/api';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = React.useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    api.getDashboardSummary()
      .then((res) => setData(res))
      .catch((err) => console.warn('Dashboard fetch error:', err))
      .finally(() => setLoading(false));
  }, []);

  const d = data || {
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
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-200">
      {/* 1. Welcome Hero Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary-900 via-primary-800 to-indigo-900 text-white p-7 shadow-lg">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-[11px] font-bold tracking-wider uppercase text-primary-200">
            <Sparkles className="w-3.5 h-3.5 text-primary-300" />
            Overview & Defense Pipeline
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Good morning, Maya Lin
          </h1>
          <p className="text-sm text-primary-100/90 leading-relaxed font-normal">
            You are 2 modules away from completing <span className="font-semibold text-white">Causal Inference</span> and qualifying for your Capstone Oral Defense.
          </p>
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              variant="primary"
              size="md"
              className="bg-white text-primary-900 hover:bg-primary-50 font-bold shadow-md shadow-black/10"
              onClick={() => navigate('/app/reader')}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Resume Module 3
            </Button>
            <Button
              variant="outline"
              size="md"
              className="bg-white/10 hover:bg-white/20 text-white border-white/20"
              onClick={() => navigate('/app/intake')}
            >
              Explore new topic
            </Button>
          </div>
        </div>

        {/* Decorative backdrop shapes */}
        <div className="absolute -right-10 -bottom-10 w-64 h-64 rounded-full bg-primary-500/20 blur-3xl pointer-events-none" />
        <div className="absolute right-20 top-0 w-48 h-48 rounded-full bg-indigo-400/10 blur-2xl pointer-events-none" />
      </div>

      {/* 2. Four Key Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase tracking-wider">
            <span>Active Subjects</span>
            <BookOpen className="w-4 h-4 text-primary-600" />
          </div>
          <div className="my-2">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">3</div>
            <div className="text-xs text-slate-500 font-medium">In progress across 18 modules</div>
          </div>
          <div className="w-full bg-slate-100 h-1 rounded-full overflow-hidden">
            <div className="bg-primary-600 h-full w-2/3" />
          </div>
        </Card>

        {/* Metric 2 */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase tracking-wider">
            <span>Oral Defenses Passed</span>
            <Mic className="w-4 h-4 text-purple-600" />
          </div>
          <div className="my-2 flex items-baseline justify-between">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">12</div>
            <Badge variant="success" size="sm">+3 this month</Badge>
          </div>
          <div className="text-xs text-slate-500 font-medium">Certified milestones</div>
        </Card>

        {/* Metric 3 */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase tracking-wider">
            <span>Reasoning Depth</span>
            <Brain className="w-4 h-4 text-amber-500" />
          </div>
          <div className="my-2 flex items-baseline justify-between">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">88%</div>
            <Badge variant="warning" size="sm">First-Principles</Badge>
          </div>
          <div className="text-xs text-slate-500 font-medium">Bloom Level 5 (Synthesis)</div>
        </Card>

        {/* Metric 4 */}
        <Card className="p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 text-xs font-bold uppercase tracking-wider">
            <span>Weekly Focus</span>
            <Clock className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="my-2 flex items-baseline gap-1">
            <div className="text-3xl font-extrabold text-slate-900 font-mono">6.4</div>
            <span className="text-sm font-semibold text-slate-500">hrs</span>
          </div>
          <div className="text-xs text-slate-500 font-medium">Active inquiry & defense</div>
        </Card>
      </div>

      {/* 3. Main Grid: Left (Learning Paths & Inquiries) + Right (Upcoming Defense & Rhythm) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Section: In Progress Learning Paths */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-primary-600">
                  Curriculum Trajectory
                </span>
                <h2 className="text-base font-bold text-slate-900">
                  In Progress Learning Paths
                </h2>
              </div>
              <button
                onClick={() => navigate('/app/roadmap')}
                className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1"
              >
                View all curricula <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Path Card 1 */}
            <Card hoverable className="p-5 space-y-4" onClick={() => navigate('/app/reader')}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="cyan" size="sm">Applied Level</Badge>
                    <span className="text-xs text-slate-400 font-medium">
                      Module 03 &bull; Hypothesis Testing & LRT
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900">
                    Statistics for Decisions: Neyman–Pearson Lemma
                  </h3>
                </div>
                <span className="text-xs text-slate-400 whitespace-nowrap font-medium">
                  Last active 42 mins ago
                </span>
              </div>

              {/* Progress bar and badges */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-600">4 of 6 concepts defended</span>
                  <span className="text-primary-600 font-mono">66% Phase Progress</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '66%' }} />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1 text-xs">
                <div className="flex items-center gap-1.5 text-emerald-600 font-medium">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Prerequisite: Probability Bounds met</span>
                </div>
                <span className="font-bold text-primary-600 flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                  Continue dialogue &rarr;
                </span>
              </div>
            </Card>

            {/* Path Card 2 */}
            <Card hoverable className="p-5 space-y-4" onClick={() => navigate('/app/reader')}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="purple" size="sm">Rigorous Level</Badge>
                    <span className="text-xs text-slate-400 font-medium">
                      Module 02 &bull; Backdoor Criterion & DAGs
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900">
                    Causal Inference & Potential Outcomes
                  </h3>
                </div>
                <span className="text-xs text-slate-400 whitespace-nowrap font-medium">
                  Last active yesterday
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-600">1 of 6 concepts defended</span>
                  <span className="text-purple-600 font-mono">17% Phase Progress</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: '17%' }} />
                </div>
              </div>

              <div className="flex items-center justify-between pt-1 text-xs">
                <div className="flex items-center gap-1.5 text-amber-600 font-medium">
                  <AlertCircle className="w-4 h-4" />
                  <span>1 unresolved counter-argument</span>
                </div>
                <span className="font-bold text-primary-600 flex items-center gap-1">
                  Continue dialogue &rarr;
                </span>
              </div>
            </Card>
          </div>

          {/* Section: Recent Socratic Inquiries */}
          <div className="space-y-3">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Dialectic History
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Recent Socratic Inquiries
              </h2>
              <p className="text-xs text-slate-500">
                Probing questions explored during active reading and oral checks
              </p>
            </div>

            <div className="space-y-3">
              {/* Inquiry 1 */}
              <Card className="p-4 space-y-2 border-l-4 border-l-primary-600">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900">Monotone Likelihood</span>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">Today, 10:15 AM</span>
                    <Badge variant="success" size="sm">Mastered</Badge>
                  </div>
                </div>
                <p className="text-xs text-slate-700 italic font-medium leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  &ldquo;If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?&rdquo;
                </p>
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-500">
                    Resolution through <strong className="text-slate-700">Karlin-Rubin Theorem</strong>
                  </span>
                  <button className="text-primary-600 font-semibold hover:underline">
                    Revisit transcript
                  </button>
                </div>
              </Card>

              {/* Inquiry 2 */}
              <Card className="p-4 space-y-2 border-l-4 border-l-amber-500">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900">Causal DAGs</span>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-400 font-mono">Oct 22, 16:40</span>
                    <Badge variant="warning" size="sm">In Progress</Badge>
                  </div>
                </div>
                <p className="text-xs text-slate-700 italic font-medium leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  &ldquo;Why does unobserved confounding invalidate backdoor adjustment even when sample size n &rarr; &infin;?&rdquo;
                </p>
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-slate-500">
                    Asymptotic bias vs variance distinction
                  </span>
                  <button className="text-primary-600 font-semibold hover:underline">
                    Revisit transcript
                  </button>
                </div>
              </Card>
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): Upcoming Defense & Cognitive Rhythm */}
        <div className="space-y-6">
          {/* Upcoming Defense Card */}
          <Card className="p-5 border-primary-200 bg-gradient-to-b from-primary-50/60 to-white space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-primary-700">
                Upcoming Defense
              </span>
              <Badge variant="primary" size="sm">Tomorrow at 10:00 AM</Badge>
            </div>

            <div>
              <h3 className="text-base font-extrabold text-slate-900 leading-snug">
                Neyman–Pearson LRT & Error Bounds
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Module 03 Capstone Validation
              </p>
            </div>

            <div className="flex items-center gap-3 p-3 rounded-xl bg-white border border-slate-200/80 shadow-xs">
              <Avatar name="Julian Vance" size="md" />
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold text-slate-900">Dr. Julian Vance</div>
                <div className="text-[11px] text-slate-400">Lead Examiner &bull; Decision Theory</div>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.
            </p>

            <Button
              variant="primary"
              size="md"
              className="w-full"
              onClick={() => navigate('/app/exam')}
              leftIcon={<Mic className="w-4 h-4" />}
            >
              Enter Defense Chamber
            </Button>
          </Card>

          {/* Weekly Inquiry Rhythm */}
          <Card className="p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Cognitive Load
                </span>
                <h3 className="text-sm font-bold text-slate-900">
                  Weekly Inquiry Rhythm
                </h3>
              </div>
              <BarChart3 className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-xs text-slate-500">
              Active dialogue & deep reading time
            </p>

            {/* Simple CSS Bar Chart for 7 days */}
            <div className="h-28 flex items-end justify-between gap-2 pt-4 px-2">
              {[
                { day: 'Mon', h: '60%', active: false },
                { day: 'Tue', h: '45%', active: false },
                { day: 'Wed', h: '85%', active: true },
                { day: 'Thu', h: '70%', active: false },
                { day: 'Fri', h: '95%', active: false },
                { day: 'Sat', h: '30%', active: false },
                { day: 'Sun', h: '50%', active: false },
              ].map((item) => (
                <div key={item.day} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <div
                    className={`w-full rounded-t-md transition-all ${
                      item.active ? 'bg-primary-600' : 'bg-slate-200 hover:bg-slate-300'
                    }`}
                    style={{ height: item.h }}
                  />
                  <span className="text-[10px] text-slate-400 font-mono">{item.day}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
