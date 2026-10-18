import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  Calendar,
  ShieldCheck,
  Edit3,
  Share2,
  GitFork,
  Sigma,
  Compass,
  Binary,
  ArrowRight,
  UserCheck,
  Radio,
  Clock,
  Mic,
  Lock,
} from 'lucide-react';
import { Card } from '../components/atoms/Card';

interface MasteredSubject {
  id: string;
  title: string;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  date: string;
  examiner: string;
  badgeType: string;
  score: number;
  tiers: number;
  maxTiers: number;
}

interface OralProbe {
  id: string;
  question: string;
  excerpt: string;
  defenseTag: string;
  badge: string;
  badgeColor: string;
  duration: string;
}

export const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'mastered' | 'transcripts' | 'heatmap'>('mastered');

  const masteredSubjects: MasteredSubject[] = [
    {
      id: 'sub-1',
      title: 'Causal Inference & Potential Outcomes',
      icon: GitFork,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-600',
      date: 'Oct 23, 2024',
      examiner: 'Assay AI',
      badgeType: 'SYNTHESIS & RIGOR',
      score: 94,
      tiers: 5,
      maxTiers: 5,
    },
    {
      id: 'sub-2',
      title: 'Neyman–Pearson Hypothesis Testing',
      icon: Sigma,
      iconBg: 'bg-purple-50',
      iconColor: 'text-purple-600',
      date: 'Sep 14, 2024',
      examiner: 'Lead Dr. Elena Rostova',
      badgeType: 'FORMAL DISTINCTION',
      score: 96,
      tiers: 5,
      maxTiers: 5,
    },
    {
      id: 'sub-3',
      title: 'Epistemology of Artificial Reason',
      icon: Compass,
      iconBg: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
      date: 'Aug 02, 2024',
      examiner: 'Assay AI',
      badgeType: 'DIALECTIC MASTERY',
      score: 91,
      tiers: 5,
      maxTiers: 5,
    },
    {
      id: 'sub-4',
      title: 'Algorithmic Information & Kolmogorov Bounds',
      icon: Binary,
      iconBg: 'bg-sky-50',
      iconColor: 'text-sky-600',
      date: 'Jul 18, 2024',
      examiner: 'Lead Dr. Marcus Thorne',
      badgeType: 'SYNTHESIS & RIGOR',
      score: 95,
      tiers: 5,
      maxTiers: 5,
    },
  ];

  const oralProbes: OralProbe[] = [
    {
      id: 'probe-1',
      question: '“Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?”',
      excerpt:
        'Rafida proved conditional non-identifiability via non-zero residual covariances in the unobserved path, demonstrating that asymptotic sample volume cannot bridge topological confounding.',
      defenseTag: 'Causal DAGs · Defense #ASY-8921',
      badge: 'Defended with Distinction',
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200/70',
      duration: '12 mins audio dialogue',
    },
    {
      id: 'probe-2',
      question: '“If density ratio stops being strictly monotonic, does Neyman–Pearson still yield a UMP critical test?”',
      excerpt:
        'Clarified the loss of Uniformly Most Powerful status without Karlin-Rubin MLR preservation, demonstrating piecewise randomization boundary definitions.',
      defenseTag: 'Neyman–Pearson Lemma · Defense #ASY-8412',
      badge: 'Mastered',
      badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200/70',
      duration: '18 mins audio dialogue',
    },
    {
      id: 'probe-3',
      question: '“Under what conditions does the exclusion restriction break down in two-stage least squares?”',
      excerpt:
        'Demonstrated violation mechanisms through direct instrument-outcome pathways and unmeasured instrument-confounder feedback loops.',
      defenseTag: 'Instrumental Variables · Defense #ASY-7901',
      badge: 'Proficient',
      badgeColor: 'bg-indigo-50 text-indigo-700 border-indigo-200/70',
      duration: '22 mins audio dialogue',
    },
  ];

  const radarMetrics = [
    { label: 'Concept Recall', score: 95 },
    { label: 'Logical Consistency', score: 94 },
    { label: 'Evidence Synthesis', score: 92 },
    { label: 'Epistemic Humility', score: 90 },
    { label: 'Adversarial Defense', score: 88 },
  ];

  // Radar chart mathematical coordinate calculation
  // 5 vertices: Logical (top, -90deg), Synthesis (-18deg), Defense (54deg), Humility (126deg), Recall (198deg)
  const center = 140;
  const maxRadius = 85;
  const angles = [-90, -18, 54, 126, 198]; // in degrees
  const axisLabels = ['LOGICAL', 'SYNTHESIS', 'DEFENSE', 'HUMILITY', 'RECALL'];
  const values = [0.94, 0.92, 0.88, 0.90, 0.95];

  const getCoordinates = (angleDeg: number, radius: number) => {
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: center + radius * Math.cos(rad),
      y: center + radius * Math.sin(rad),
    };
  };

  const getPentagonPoints = (radius: number) => {
    return angles
      .map((deg) => {
        const { x, y } = getCoordinates(deg, radius);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  };

  const radarPoints = angles
    .map((deg, i) => {
      const { x, y } = getCoordinates(deg, maxRadius * values[i]);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16 animate-in fade-in duration-200">
      {/* 1. Profile Hero Card */}
      <Card className="p-6 sm:p-7 bg-white shadow-card border border-slate-200/80">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start sm:items-center gap-5">
            {/* Avatar */}
            <img
              src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=160&auto=format&fit=crop&q=80"
              alt="Rafida Aziz"
              className="w-20 h-20 rounded-full object-cover ring-4 ring-slate-100 shadow-sm shrink-0"
            />
            <div className="space-y-1.5">
              <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-100/80">
                LEVEL 4 COGNITIVE FELLOW
              </span>
              <div className="flex items-baseline gap-2">
                <h1 className="text-2xl font-black text-slate-900 tracking-tight">Rafida Aziz</h1>
                <span className="text-sm font-medium text-slate-400">@rafidaaziz</span>
              </div>
              <p className="text-xs text-slate-600 max-w-xl leading-relaxed">
                Curious researcher exploring algorithm complexity, data structures, and foundational computer science.
              </p>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  San Francisco, CA
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  Member since Mar 2026
                </span>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/70 text-[11px] font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  Verified Fellow
                </span>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2.5 shrink-0 self-start md:self-center">
            <button
              onClick={() => navigate('/app/settings')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Profile</span>
            </button>
            <button
              onClick={() => alert('Dossier link copied to clipboard: https://assay.dialectic.edu/dossier/rafidaaziz')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Share Public Dossier</span>
            </button>
          </div>
        </div>
      </Card>

      {/* 2. Navigation Tabs & Verification Note */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="inline-flex items-center p-1 bg-slate-100/90 rounded-xl border border-slate-200/60 self-start">
          <button
            onClick={() => setActiveTab('mastered')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'mastered'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Mastered Subjects (14)
          </button>
          <button
            onClick={() => setActiveTab('transcripts')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'transcripts'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Oral Defense Transcripts
          </button>
          <button
            onClick={() => setActiveTab('heatmap')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'heatmap'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            Activity Heatmap
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
          <span>Publicly verifiable by academic cryptographic attestations</span>
        </div>
      </div>

      {/* 3. Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (8 cols): Mastered Subjects & Notable Oral Probes */}
        <div className="lg:col-span-8 space-y-8">
          {/* Mastered Subjects Section */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-slate-900">Mastered Subjects</h2>
                <p className="text-xs text-slate-400 font-normal">
                  Peer-blinded oral defense certifications and lemmas
                </p>
              </div>
              <button
                onClick={() => navigate('/app/report')}
                className="text-xs font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 cursor-pointer"
              >
                <span>View all 14 certifications</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* 2x2 Grid of Subject Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {masteredSubjects.map((sub) => {
                const IconComponent = sub.icon;
                return (
                  <Card key={sub.id} className="p-5 bg-white shadow-card border border-slate-200/80 flex flex-col justify-between hover:border-slate-300 transition-all">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="font-bold text-sm text-slate-900 leading-snug line-clamp-2">
                          {sub.title}
                        </h3>
                        <div className={`p-2 rounded-xl shrink-0 ${sub.iconBg} ${sub.iconColor}`}>
                          <IconComponent className="w-4 h-4" />
                        </div>
                      </div>

                      <p className="text-[11px] text-slate-400">
                        Defended {sub.date} &bull; {sub.examiner}
                      </p>

                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
                          {sub.badgeType}
                        </span>
                        <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
                          ORAL SCORE: {sub.score}/100
                        </span>
                      </div>

                      {/* Defense Competency Matrix */}
                      <div className="space-y-1.5 pt-1">
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="text-slate-400 font-medium">Defense Competency Matrix</span>
                          <span className="font-bold text-slate-800">{sub.tiers} / {sub.maxTiers} Tiers</span>
                        </div>
                        <div className="flex gap-1.5">
                          {Array.from({ length: sub.maxTiers }).map((_, idx) => (
                            <div
                              key={idx}
                              className={`h-1.5 rounded-full flex-1 transition-all ${
                                idx < sub.tiers ? 'bg-indigo-600' : 'bg-slate-200'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => navigate('/app/report')}
                      className="mt-5 w-full bg-[#0F172A] hover:bg-slate-800 text-white rounded-xl py-2.5 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <span>View Dossier</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </Card>
                );
              })}
            </div>
          </section>

          {/* Notable Oral Exam Probes Section */}
          <section className="space-y-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Notable Oral Exam Probes</h2>
              <p className="text-xs text-slate-400 font-normal">
                Recent dialectic excerpts and examiner challenges
              </p>
            </div>

            <div className="space-y-3">
              {oralProbes.map((probe) => (
                <Card key={probe.id} className="p-5 bg-white shadow-card border border-slate-200/80 hover:border-slate-300 transition-all">
                  <div className="flex items-start gap-4">
                    <div className="w-9 h-9 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 mt-0.5">
                      <UserCheck className="w-4 h-4" />
                    </div>
                    <div className="space-y-2 flex-1">
                      <h4 className="text-xs font-bold text-slate-900 leading-snug">
                        {probe.question}
                      </h4>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {probe.excerpt}
                      </p>

                      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-100 text-[11px]">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">{probe.defenseTag}</span>
                          <span className="text-slate-300">&bull;</span>
                          <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold ${probe.badgeColor}`}>
                            {probe.badge}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5 text-slate-500 font-medium">
                          <Radio className="w-3.5 h-3.5 text-slate-400" />
                          <span>{probe.duration}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column (4 cols): Cognitive Architecture & Portfolio Telemetry */}
        <div className="lg:col-span-4 space-y-6">
          {/* Card 1: Bloom Taxonomy Radar */}
          <Card className="p-6 bg-white shadow-card border border-slate-200/80 space-y-5">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-primary-600">
                COGNITIVE ARCHITECTURE
              </span>
              <h3 className="text-base font-bold text-slate-900 mt-0.5">Bloom Taxonomy Radar</h3>
              <p className="text-xs text-slate-400 font-normal leading-relaxed">
                Continuous evaluation across oral defense transcripts
              </p>
            </div>

            {/* Radar Spider Chart Canvas */}
            <div className="relative flex items-center justify-center py-2">
              <svg viewBox="0 0 280 280" className="w-full max-w-[260px] h-auto overflow-visible select-none">
                {/* Concentric reference pentagons */}
                {[0.25, 0.5, 0.75, 1.0].map((scale, i) => (
                  <polygon
                    key={i}
                    points={getPentagonPoints(maxRadius * scale)}
                    fill="none"
                    stroke="#E2E8F0"
                    strokeWidth="1"
                    strokeDasharray={scale === 1.0 ? 'none' : '3 3'}
                  />
                ))}

                {/* Radial axes */}
                {angles.map((deg, i) => {
                  const { x, y } = getCoordinates(deg, maxRadius);
                  return (
                    <line
                      key={i}
                      x1={center}
                      y1={center}
                      x2={x}
                      y2={y}
                      stroke="#E2E8F0"
                      strokeWidth="1"
                    />
                  );
                })}

                {/* Filled radar data polygon */}
                <polygon
                  points={radarPoints}
                  fill="rgba(79, 70, 229, 0.12)"
                  stroke="#4F46E5"
                  strokeWidth="2.5"
                />

                {/* Data points on vertices */}
                {angles.map((deg, i) => {
                  const { x, y } = getCoordinates(deg, maxRadius * values[i]);
                  return (
                    <circle
                      key={i}
                      cx={x}
                      cy={y}
                      r="4"
                      fill="#4F46E5"
                      stroke="#FFFFFF"
                      strokeWidth="2"
                    />
                  );
                })}

                {/* Axis Labels outside the polygon */}
                {angles.map((deg, i) => {
                  const { x, y } = getCoordinates(deg, maxRadius + 18);
                  return (
                    <text
                      key={i}
                      x={x}
                      y={y + 4}
                      fill="#64748B"
                      fontSize="9"
                      fontWeight="700"
                      textAnchor="middle"
                      fontFamily="sans-serif"
                    >
                      {axisLabels[i]}
                    </text>
                  );
                })}
              </svg>
            </div>

            {/* Dimension Breakdown Metrics */}
            <div className="space-y-1.5 pt-2 border-t border-slate-100">
              {radarMetrics.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-slate-50/80 px-3 py-2 rounded-xl flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary-600 shrink-0" />
                    <span className="text-slate-700 font-medium">{item.label}</span>
                  </div>
                  <span className="font-mono font-bold text-slate-900">{item.score}%</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Card 2: Portfolio Telemetry / Verified Metrics */}
          <Card className="p-6 bg-white shadow-card border border-slate-200/80 space-y-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-primary-600">
                PORTFOLIO TELEMETRY
              </span>
              <h3 className="text-base font-bold text-slate-900 mt-0.5">Verified Metrics</h3>
            </div>

            <div className="space-y-3">
              {/* Metric 1 */}
              <div className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-start gap-3.5">
                <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 shrink-0 mt-0.5">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xl font-black text-slate-900 font-mono">148</span>
                    <span className="text-xs font-bold text-slate-500">Total Hours</span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-normal mt-0.5">
                    Active Socratic dialogue & deep inquiry time
                  </p>
                </div>
              </div>

              {/* Metric 2 */}
              <div className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-start gap-3.5">
                <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 shrink-0 mt-0.5">
                  <Mic className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xl font-black text-slate-900 font-mono">36</span>
                    <span className="text-xs font-bold text-slate-500">Socratic Rounds</span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-normal mt-0.5">
                    Live examiner examinations completed across 14 modules
                  </p>
                </div>
              </div>

              {/* Metric 3 */}
              <div className="p-3.5 rounded-2xl bg-slate-50/80 border border-slate-100 flex items-start gap-3.5">
                <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 shrink-0 mt-0.5">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-xl font-black text-slate-900 font-mono">98.4%</span>
                    <span className="text-xs font-bold text-slate-500">Integrity Index</span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-normal mt-0.5">
                    Peer-blinded verified integrity standard
                  </p>
                </div>
              </div>
            </div>

            {/* Cryptographic attestation footer */}
            <div className="pt-2 flex items-center justify-center gap-1.5 text-[11px] text-slate-400">
              <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span>Cryptographic attestation signed by Cambridge Dialectic Node</span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
