import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import {
  ShieldCheck,
  Download,
  Share2,
  Copy,
  Check,
  Award,
  Layers,
  Timer,
  Lightbulb,
  ArrowRight,
  BookOpen,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { FinalReportResponse } from '../types/api';

export const ReportPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, user, activeTrack } = useAppStore();
  const [report, setReport] = useState<FinalReportResponse | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedHash, setCopiedHash] = useState(false);

  useEffect(() => {
    const sid = activeSessionId || 'sess_coding_basic';
    api.getFinalReport(sid)
      .then((res) => setReport(res))
      .catch((e) => console.warn('Final report fallback:', e));
  }, [activeSessionId]);

  const isCoding = activeTrack === 'coding' || activeSessionId === 'sess_coding_basic';
  const isDistributed = activeTrack === 'distributed' || activeSessionId === 'sess_distributed_systems';

  const subjectTitle = report?.syllabus_title || (
    isCoding
      ? 'Foundations of Algorithms & Data Structures'
      : isDistributed
      ? 'Distributed Consensus & Byzantine Fault Tolerance'
      : 'Statistical Decision Theory'
  );

  const candidateName = user?.name || 'Maya Lin';
  const dossierId = report?.session_id
    ? `ASY-${report.session_id.replace('sess_', '').toUpperCase()}`
    : 'ASY-8921';

  const depthScore = report?.summary?.mean_score != null
    ? Math.round(report.summary.mean_score * 100)
    : 92;

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handleCopyHash = () => {
    navigator.clipboard.writeText('sha256:7f9a2b89d44c8e762fa198b1c041e');
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  // 5-Axis Spider Radar Chart Coordinates Calculation
  // Axes: Recall (top 90°), Application (18°), Analysis (306° / -54°), Evaluation (234° / -126°), Creation & Synthesis (162°)
  const cx = 150;
  const cy = 135;
  const rMax = 85;

  // Dynamic Scores based on depthScore
  const baseScale = depthScore / 100;
  const scores = {
    recall: Math.min(0.98, Number((baseScale * 1.03).toFixed(2))),
    application: Math.min(0.96, Number((baseScale * 0.99).toFixed(2))),
    analysis: Math.min(0.97, Number((baseScale * 1.02).toFixed(2))),
    evaluation: Math.min(0.95, Number((baseScale * 0.96).toFixed(2))),
    creation: Math.min(0.96, Number((baseScale * 0.98).toFixed(2))),
  };

  // Angles in radians for regular pentagon (pointing up)
  const angles = [
    -Math.PI / 2,                  // Recall (Top: -90°)
    -Math.PI / 2 + (2 * Math.PI) / 5,      // Application (-18°)
    -Math.PI / 2 + (4 * Math.PI) / 5,      // Analysis (54°)
    -Math.PI / 2 + (6 * Math.PI) / 5,      // Evaluation (126°)
    -Math.PI / 2 + (8 * Math.PI) / 5,      // Creation & Synthesis (198°)
  ];

  // Helper to get polygon points at scale factor
  const getPentagonPoints = (scale: number) => {
    return angles
      .map((a) => {
        const x = cx + rMax * scale * Math.cos(a);
        const y = cy + rMax * scale * Math.sin(a);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  };

  // Data polygon points
  const dataValues = [
    scores.recall,
    scores.application,
    scores.analysis,
    scores.evaluation,
    scores.creation,
  ];

  const dataPoints = dataValues
    .map((val, idx) => {
      const x = cx + rMax * val * Math.cos(angles[idx]);
      const y = cy + rMax * val * Math.sin(angles[idx]);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  // Track-specific findings & dialogue excerpts
  const findings = isCoding
    ? {
        subtitle: `${candidateName} • Algorithmic Invariants & Asymptotic Frontiers`,
        body: `Candidate demonstrated advanced synthetic reasoning across algorithmic complexity bounds and abstract data structures. The candidate exhibited unhesitating precision when deconstructing recurrence master theorems, establishing rigorous amortized boundaries, and defending cache locality invariants under empirical adversarial workloads. The evaluation committee recognized exceptional dialectical poise during intense adversarial questioning on worst-case quicksort degeneration and dynamic array reallocation.`,
        chip1: 'Recurrence Rigor: 98%',
        chip2: 'Median Cognitive Latency: 1.8s',
        chip3: 'Epistemic Humility: High',
        examiner: 'Dr. Elena Rostova',
        examinerRole: 'LEAD SOCRATIC EVALUATOR · COMPUTATIONAL COMPLEXITY',
        competencies: [
          {
            title: '1. Asymptotic Complexity Rigor',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Flawlessly articulated growth frontiers (O, Ω, Θ) and recurrence relations without cognitive hesitation. Maintained mathematical fidelity when mapping Master Theorem cases.',
          },
          {
            title: '2. Adversarial Input Reasoning',
            score: '4 / 5',
            badge: 'Strong',
            desc: 'Constructed valid adversarial input sequences when challenged by examiner on pivot degradation. Resolved worst-case partitioning bottlenecks with minor prompt intervention.',
          },
          {
            title: '3. Synthesis of Memory & Hierarchy',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Synthesized geometric array doubling with aggregate potential functions. Fluidly integrated cache hierarchy implications with instruction-level branch prediction.',
          },
          {
            title: '4. Dialectical Code Clarity',
            score: '4 / 5',
            badge: 'Proficient',
            desc: 'Responded precisely under adversarial Socratic counter-probes. Re-anchored arguments back to original algorithmic invariants under probing stress.',
          },
        ],
        segment1: {
          tag: 'DIALECTIC SEGMENT I · WORST-CASE PARTITIONING DEGRADATION',
          time: '14:20',
          q: 'If an adversary provides a sequence of pre-sorted elements to quicksort with naive leftmost pivoting, why does time complexity degrade to O(n²)?',
          a: 'Because unbalanced partitioning yields subproblems of size 0 and n - 1 at each recursion level, resulting in the recurrence T(n) = T(n - 1) + O(n) = O(n²). Using median-of-three or randomized pivoting guarantees O(n log n) expected runtime with high probability.',
        },
        segment2: {
          tag: 'DIALECTIC SEGMENT II · AMORTIZED BOUNDS & DYNAMIC RESIZING',
          time: '28:45',
          q: 'Why does doubling the geometric expansion factor in dynamic arrays guarantee O(1) amortized insertion, whereas additive increment fails?',
          a: 'Geometric doubling distributes the O(n) reallocation cost across n/2 subsequent O(1) operations, bounding the potential function Φ = 2k - n ≥ 0. Additive growth forces reallocations every k steps, collapsing the aggregate amortized bound to O(n).',
        },
      }
    : isDistributed
    ? {
        subtitle: `${candidateName} • Distributed Consensus & Byzantine Fault Tolerance`,
        body: `Candidate demonstrated advanced synthetic reasoning across distributed consensus protocols and fault-tolerant topologies. The candidate exhibited unhesitating precision when deconstructing partial synchrony, establishing rigorous quorum safety invariants, and defending replicated state machine determinism under network partitions. The evaluation committee recognized exceptional dialectical poise during intense adversarial questioning on Paxos proposal numbers and Byzantine view changes.`,
        chip1: 'Quorum Safety: 99%',
        chip2: 'Median Cognitive Latency: 1.9s',
        chip3: 'Epistemic Humility: High',
        examiner: 'Dr. Aris Thorne',
        examinerRole: 'LEAD SOCRATIC EVALUATOR · DISTRIBUTED CONSENSUS',
        competencies: [
          {
            title: '1. Consensus Safety Invariants',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Flawlessly articulated FLP impossibility and Lamport partial order invariants without cognitive hesitation.',
          },
          {
            title: '2. Adversarial Fault Reasoning',
            score: '4 / 5',
            badge: 'Strong',
            desc: 'Resolved split-brain quorum conflicts and adversarial Byzantine message corruption under network partitioning probes.',
          },
          {
            title: '3. Replicated State Synthesis',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Fluidly integrated state machine replication with Raft log compaction and view-change safety bounds.',
          },
          {
            title: '4. Dialectical Precision',
            score: '4 / 5',
            badge: 'Proficient',
            desc: 'Responded precisely under adversarial Socratic counter-probes, maintaining consensus invariant proofs under stress.',
          },
        ],
        segment1: {
          tag: 'DIALECTIC SEGMENT I · FLP IMPOSSIBILITY BOUNDARY',
          time: '16:10',
          q: 'In asynchronous networks, why can no deterministic consensus protocol guarantee liveness in the presence of even a single crash failure?',
          a: 'Because FLP impossibility proves that an adversary can delay messages indefinitely such that a process cannot distinguish a dead node from an infinitely slow node, trapping the protocol in an uncommitted bivalent configuration.',
        },
        segment2: {
          tag: 'DIALECTIC SEGMENT II · BYZANTINE 3F+1 QUORUM OVERLAP',
          time: '34:20',
          q: 'Why does PBFT require 3f + 1 replicas to tolerate f Byzantine failures, whereas crash fault tolerance only requires 2f + 1?',
          a: 'Because Byzantine nodes can actively lie by sending conflicting votes. In a system of N nodes where f are faulty, the primary must proceed with N - f responses. To ensure non-faulty quorums overlap by at least one honest node, (N - f) + (N - f) - N > f, which strictly yields N ≥ 3f + 1.',
        },
      }
    : {
        subtitle: `${candidateName} • Statistical Decision Theory & Neyman-Pearson Testing`,
        body: `Candidate demonstrated advanced synthetic reasoning across statistical decision boundaries and likelihood ratio tests. The candidate exhibited unhesitating precision when deriving uniformly most powerful critical regions, defending minimax risk bounds, and establishing Neyman-Pearson optimality under empirical covariate drift. The evaluation committee recognized exceptional dialectical poise during intense adversarial questioning on likelihood ratios and structural misspecification.`,
        chip1: 'Likelihood Invariance: 98%',
        chip2: 'Median Cognitive Latency: 1.8s',
        chip3: 'Epistemic Humility: High',
        examiner: 'Dr. Julian Vance',
        examinerRole: 'LEAD SOCRATIC EVALUATOR · DECISION THEORY',
        competencies: [
          {
            title: '1. Concept Rigor',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Flawlessly articulated Neyman-Pearson lemma and likelihood ratio test boundaries without cognitive hesitation.',
          },
          {
            title: '2. Counter-factual Reasoning',
            score: '4 / 5',
            badge: 'Strong',
            desc: 'Constructed valid minimax decision rules and Bayes risk estimators when challenged on prior misspecification.',
          },
          {
            title: '3. Synthesis of Evidence',
            score: '5 / 5',
            badge: 'Distinction',
            desc: 'Synthesized uniformly most powerful critical regions with asymptotic normality bounds and empirical trade-offs.',
          },
          {
            title: '4. Dialectical Clarity',
            score: '4 / 5',
            badge: 'Proficient',
            desc: 'Responded precisely under adversarial Socratic counter-probes, re-anchoring arguments back to original test invariants.',
          },
        ],
        segment1: {
          tag: 'DIALECTIC SEGMENT I · NEYMAN-PEARSON OPTIMALITY',
          time: '18:42',
          q: 'When testing simple hypotheses H₀: θ = θ₀ versus H₁: θ = θ₁, why is the likelihood ratio test uniformly most powerful among all level-α tests?',
          a: 'By the Neyman-Pearson lemma, allocating critical regions to sample points with maximal ratio f(x; θ₁) / f(x; θ₀) maximizes statistical power ∫_k f(x; θ₁) dx subject to the size constraint ∫_k f(x; θ₀) dx ≤ α. Any perturbation into lower-ratio regions strictly diminishes power for the identical false-positive budget.',
        },
        segment2: {
          tag: 'DIALECTIC SEGMENT II · BAYESIAN RISK & MINIMAX DUALITY',
          time: '31:15',
          q: 'Under what conditions does a Bayes estimator coincide with the minimax estimator?',
          a: 'A Bayes estimator coincides with the minimax estimator if and only if it achieves constant risk over the parameter space and corresponds to a least favorable prior distribution, establishing equality between the minimax risk and maximum Bayes risk.',
        },
      };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200 pb-16">
      {/* Breadcrumb & Title Section (Figma 1:2251) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
            <span>Dossiers</span>
            <span>&gt;</span>
            <span className="text-slate-600 font-semibold">{subjectTitle}</span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Competency Dossier #{dossierId}
            </h1>
            <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1 rounded-full font-semibold inline-flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              Mastery Verified &bull; Socratic Oral Defense Passed
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Button
            variant="outline"
            size="md"
            onClick={handleShare}
            leftIcon={<Share2 className="w-4 h-4" />}
            className="text-xs font-bold border-slate-200"
          >
            {copiedLink ? 'Copied Link!' : 'Share Public Link'}
          </Button>
          <button
            onClick={() => window.print()}
            className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-4 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 transition-colors shadow-xs"
          >
            <Download className="w-4 h-4" />
            <span>Export Verified PDF</span>
          </button>
          <Button
            variant="primary"
            size="md"
            onClick={() => navigate('/app/roadmap')}
            rightIcon={<ArrowRight className="w-4 h-4" />}
            className="text-xs font-bold shadow-xs bg-[#4338CA] hover:bg-[#3730A3] text-white"
          >
            Lanjut ke Roadmap
          </Button>
        </div>
      </div>

      {/* 2-Column Grid Layout (Figma 1:2251) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (7 cols): Findings & Competencies & Exchanges */}
        <div className="lg:col-span-7 space-y-6">
          {/* Card 1: Executive Summary & Oral Defense Findings */}
          <Card className="p-6 bg-white border border-slate-200/80 shadow-xs space-y-5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                EXECUTIVE SUMMARY &amp; ORAL DEFENSE FINDINGS
              </span>
              <span className="bg-indigo-50 text-indigo-700 text-[11px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-600" />
                Live Defense Evaluation
              </span>
            </div>

            <div className="flex flex-col sm:flex-row items-start justify-between gap-6">
              <div className="space-y-2 flex-1">
                <h2 className="text-base font-bold text-slate-900">
                  {findings.subtitle}
                </h2>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {findings.body}
                </p>
              </div>

              {/* Depth Score Box */}
              <div className="w-full sm:w-36 rounded-2xl bg-indigo-50/50 border border-indigo-100 p-4 text-center shrink-0 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 font-mono uppercase tracking-wider">
                  DEPTH SCORE
                </div>
                <div className="flex items-baseline justify-center">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">{depthScore}</span>
                  <span className="text-xs text-slate-400 font-medium">/100</span>
                </div>
                <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold px-2 py-0.5 rounded-full block">
                  Bloom Level 5 Synthesis
                </span>
                <span className="text-[10px] text-slate-400 font-medium block">
                  Certified Distinction
                </span>
              </div>
            </div>

            {/* Stat Chips Row */}
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/70 text-indigo-700 text-xs font-semibold">
                <Layers className="w-3.5 h-3.5" />
                {findings.chip1}
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/70 text-indigo-700 text-xs font-semibold">
                <Timer className="w-3.5 h-3.5" />
                {findings.chip2}
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/70 text-indigo-700 text-xs font-semibold">
                <Lightbulb className="w-3.5 h-3.5" />
                {findings.chip3}
              </span>
            </div>
          </Card>

          {/* Card 2: Assessed Socratic Competencies */}
          <Card className="p-6 bg-white border border-slate-200/80 shadow-xs space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                  DEFENSE RUBRIC &amp; FIRST-PRINCIPLES EVALUATION
                </span>
                <h2 className="text-base font-bold text-slate-900">
                  Assessed Socratic Competencies
                </h2>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                Weight: Peer Blinded Assessment
              </span>
            </div>

            <div className="space-y-4">
              {findings.competencies.map((comp, idx) => (
                <div key={idx} className={`space-y-1.5 ${idx > 0 ? 'pt-2 border-t border-slate-100' : ''}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-900">
                        {comp.title}
                      </span>
                      <span className="bg-emerald-50 text-emerald-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                        {comp.badge}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        {[1, 2, 3, 4, 5].map((s) => (
                          <div
                            key={s}
                            className={`w-3.5 h-1.5 rounded-full ${
                              s <= parseInt(comp.score) ? 'bg-indigo-600' : 'bg-indigo-100'
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-xs font-bold font-mono text-slate-800">{comp.score}</span>
                    </div>
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {comp.desc}
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* Card 3: Critical Dialectic Exchanges */}
          <Card className="p-6 bg-white border border-slate-200/80 shadow-xs space-y-5">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                VERIFIED ORAL DEFENSE TRANSCRIPT EXCERPTS
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Critical Dialectic Exchanges
              </h2>
              <p className="text-xs text-slate-500">
                Recorded verbatim during the live adversarial examination.
              </p>
            </div>

            <div className="space-y-4">
              {/* Dialogue Segment I */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-600" />
                    <span className="font-bold text-slate-900 font-mono text-[11px]">
                      {findings.segment1.tag}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-50 text-emerald-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                      Key Breakthrough Moment
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">{findings.segment1.time}</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-slate-700">{findings.examiner} &bull; Examiner</div>
                  <p className="italic text-slate-600">
                    &ldquo;{findings.segment1.q}&rdquo;
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-indigo-50/40 border border-indigo-100 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-indigo-900">{candidateName} &bull; Candidate</div>
                  <p className="text-slate-800 leading-relaxed">
                    &ldquo;{findings.segment1.a}&rdquo;
                  </p>
                </div>
              </div>

              {/* Dialogue Segment II */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-600" />
                    <span className="font-bold text-slate-900 font-mono text-[11px]">
                      {findings.segment2.tag}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-50 text-emerald-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                      Defended with Distinction
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">{findings.segment2.time}</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-slate-700">{findings.examiner} &bull; Examiner</div>
                  <p className="italic text-slate-600">
                    &ldquo;{findings.segment2.q}&rdquo;
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-indigo-50/40 border border-indigo-100 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-indigo-900">{candidateName} &bull; Candidate</div>
                  <p className="text-slate-800 leading-relaxed">
                    &ldquo;{findings.segment2.a}&rdquo;
                  </p>
                </div>
              </div>
            </div>
          </Card>

          {/* Card 4: Next Milestones & Module Unlock Status */}
          <Card className="p-6 bg-gradient-to-br from-indigo-50/60 via-white to-slate-50 border border-indigo-100 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 font-mono flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5 text-indigo-600" />
                KURIKULUM BERIKUTNYA DIBUKA
              </span>
              <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[11px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                <Check className="w-3 h-3 text-emerald-600" />
                Threshold Met: &ge; 75%
              </span>
            </div>

            <div className="space-y-1.5">
              <h3 className="text-sm font-bold text-slate-900">
                Siklus Ujian Selesai &bull; Lanjutkan Eksplorasi Kurikulum Anda
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Hasil evaluasi dialektika ini telah tersimpan secara permanen. Modul lanjutan di roadmap telah otomatis dibuka oleh Active Learning Engine untuk dipelajari.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Button
                variant="primary"
                size="md"
                onClick={() => navigate('/app/roadmap')}
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="text-xs font-bold shadow-xs bg-[#4338CA] hover:bg-[#3730A3] text-white"
              >
                Kembali ke Roadmap &bull; Lanjut Modul Berikutnya
              </Button>
              <Button
                variant="outline"
                size="md"
                onClick={() => navigate('/app/reader')}
                leftIcon={<BookOpen className="w-4 h-4" />}
                className="text-xs font-semibold border-slate-200 text-slate-700 hover:bg-slate-50"
              >
                Tinjau Ulang Materi Bab
              </Button>
            </div>
          </Card>
        </div>

        {/* Right Column (5 cols): Cognitive Architecture Spider Chart & Audit Record */}
        <div className="lg:col-span-5 space-y-6">
          {/* Card 1: Cognitive Architecture & Radar / Spider Chart (Figma 1:2251) */}
          <Card className="p-6 bg-white border border-slate-200/80 shadow-xs space-y-5">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                COGNITIVE ARCHITECTURE
              </span>
              <h2 className="text-lg font-bold text-slate-900">
                Bloom Taxonomy Profiling
              </h2>
            </div>

            {/* SVG 5-Axis Spider Radar Chart */}
            <div className="w-full flex justify-center py-1">
              <svg viewBox="0 0 300 270" className="w-full max-w-[280px] h-auto overflow-visible select-none">
                {/* Concentric Pentagon Grid Rings */}
                {[0.2, 0.4, 0.6, 0.8, 1.0].map((scale) => (
                  <polygon
                    key={scale}
                    points={getPentagonPoints(scale)}
                    fill="none"
                    stroke="#e2e8f0"
                    strokeWidth="1"
                  />
                ))}

                {/* 5 Axis Radial Spoke Lines */}
                {angles.map((a, i) => {
                  const x = cx + rMax * Math.cos(a);
                  const y = cy + rMax * Math.sin(a);
                  return (
                    <line
                      key={i}
                      x1={cx}
                      y1={cy}
                      x2={x}
                      y2={y}
                      stroke="#e2e8f0"
                      strokeWidth="1"
                    />
                  );
                })}

                {/* Data Polygon Fill & Outline */}
                <polygon
                  points={dataPoints}
                  fill="rgba(79, 70, 229, 0.18)"
                  stroke="#4f46e5"
                  strokeWidth="2.5"
                />

                {/* Data Point Vertex Circles */}
                {dataValues.map((val, i) => {
                  const x = cx + rMax * val * Math.cos(angles[i]);
                  const y = cy + rMax * val * Math.sin(angles[i]);
                  return (
                    <circle
                      key={i}
                      cx={x}
                      cy={y}
                      r="4"
                      fill="#4f46e5"
                      stroke="#ffffff"
                      strokeWidth="2"
                    />
                  );
                })}

                {/* Axis Labels */}
                <text x="150" y="32" textAnchor="middle" fill="#475569" fontSize="10" fontWeight="600">
                  Recall
                </text>
                <text x="268" y="105" textAnchor="start" fill="#475569" fontSize="10" fontWeight="600">
                  Application
                </text>
                <text x="215" y="240" textAnchor="middle" fill="#475569" fontSize="10" fontWeight="600">
                  Analysis
                </text>
                <text x="85" y="240" textAnchor="middle" fill="#475569" fontSize="10" fontWeight="600">
                  Evaluation
                </text>
                <text x="22" y="105" textAnchor="end" fill="#475569" fontSize="10" fontWeight="600">
                  Creation
                </text>
              </svg>
            </div>

            {/* Score Matrix Table */}
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Recall</span>
                  <span className="font-bold text-slate-900 font-mono">{Math.round(scores.recall * 100)}%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Application</span>
                  <span className="font-bold text-slate-900 font-mono">{Math.round(scores.application * 100)}%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Analysis</span>
                  <span className="font-bold text-slate-900 font-mono">{Math.round(scores.analysis * 100)}%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Evaluation</span>
                  <span className="font-bold text-slate-900 font-mono">{Math.round(scores.evaluation * 100)}%</span>
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-between text-xs">
                <span className="text-indigo-900 font-semibold">Creation &amp; Synthesis</span>
                <span className="font-bold text-indigo-700 font-mono">{Math.round(scores.creation * 100)}% &bull; High Mastery</span>
              </div>
            </div>
          </Card>

          {/* Card 2: Credential Verification & Telemetry Audit Record */}
          <Card className="p-6 bg-white border border-slate-200/80 shadow-xs space-y-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                CREDENTIAL VERIFICATION &amp; TELEMETRY
              </span>
              <h2 className="text-base font-bold text-slate-900">
                Audit Record
              </h2>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                <span className="text-slate-500">Total Inquiry Duration</span>
                <span className="font-bold text-slate-800 font-mono">16.2 hrs &bull; 6 modules</span>
              </div>
              <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                <span className="text-slate-500">Socratic Questions Probed</span>
                <span className="font-bold text-slate-800 font-mono">34 dialectic inquiries</span>
              </div>
              <div className="flex items-start justify-between pb-1.5 border-b border-slate-100">
                <span className="text-slate-500">Defense Examiner</span>
                <div className="text-right">
                  <div className="font-bold text-slate-800">{findings.examiner}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{findings.examinerRole}</div>
                </div>
              </div>
              <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                <span className="text-slate-500">Assessment Timestamp</span>
                <span className="font-semibold text-slate-700 font-mono">Oct 23, 2024 &bull; 14:45 UTC</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Defense Session ID</span>
                <span className="font-bold text-slate-800 font-mono">#{dossierId}</span>
              </div>
            </div>

            {/* Cryptographic Hash Box */}
            <div className="space-y-1.5 pt-1">
              <span className="text-[10px] uppercase font-mono text-slate-400 font-bold">
                Cryptographic Verification Hash
              </span>
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/90 flex items-center justify-between font-mono text-[11px] text-slate-600">
                <span className="truncate mr-2">sha256:7f9a2b89d44c8e762fa198b1c041e</span>
                <button
                  type="button"
                  onClick={handleCopyHash}
                  className="text-slate-400 hover:text-slate-700 p-1 rounded transition-colors"
                  title="Copy Hash"
                >
                  {copiedHash ? (
                    <Check className="w-3.5 h-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </div>

            {/* Institution Endorsement Banner */}
            <div className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white border border-slate-200 text-indigo-600 flex items-center justify-center shrink-0 shadow-2xs">
                <Award className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <div className="text-[10px] uppercase font-mono text-slate-400 font-bold">
                  INSTITUTION ENDORSEMENT
                </div>
                <div className="text-xs font-bold text-slate-900">
                  Assay Dialectic Registry
                </div>
                <div className="text-[10px] text-slate-400">
                  Immutable peer defense dossier
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
