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
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { FinalReportResponse } from '../types/api';

export const ReportPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId } = useAppStore();
  const [report, setReport] = useState<FinalReportResponse | null>(null);
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedHash, setCopiedHash] = useState(false);

  useEffect(() => {
    const sid = activeSessionId || 'sess_a1b2c3';
    api.getFinalReport(sid)
      .then((res) => setReport(res))
      .catch((e) => console.warn('Final report fallback:', e));
  }, [activeSessionId]);

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

  // Scores (0 to 1)
  const scores = {
    recall: 0.95,
    application: 0.92,
    analysis: 0.94,
    evaluation: 0.88,
    creation: 0.90,
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

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-200 pb-16">
      {/* Breadcrumb & Title Section (Figma 1:2251) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
            <span>Dossiers</span>
            <span>&gt;</span>
            <span className="text-slate-600 font-semibold">Causal Inference &amp; Quasi-Experiments</span>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Competency Dossier #ASY-8921
            </h1>
            <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-3 py-1 rounded-full font-semibold inline-flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              Mastery Verified &bull; Socratic Oral Defense Passed
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
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
            className="bg-[#1E2238] hover:bg-[#151828] text-white px-4 py-2.5 rounded-xl font-bold text-xs flex items-center gap-2 transition-colors shadow-xs"
          >
            <Download className="w-4 h-4" />
            <span>Export Verified PDF</span>
          </button>
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
                  Maya Lin &bull; Causal Inference &amp; Potential Outcomes
                </h2>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  Candidate demonstrated advanced synthetic reasoning across high-dimensional causal graphs. Lin exhibited unhesitating precision when deconstructing unobserved confounding, establishing rigorous non-parametric counterfactual boundaries, and defending the integrity of the Neyman-Rubin causal model under empirical covariate drift. The evaluation committee recognized exceptional dialectical poise during intense adversarial questioning on instrument monotonicity and structural misspecification.
                </p>
              </div>

              {/* Depth Score Box */}
              <div className="w-full sm:w-36 rounded-2xl bg-indigo-50/50 border border-indigo-100 p-4 text-center shrink-0 space-y-1">
                <div className="text-[10px] font-bold text-slate-400 font-mono uppercase tracking-wider">
                  DEPTH SCORE
                </div>
                <div className="flex items-baseline justify-center">
                  <span className="text-3xl font-extrabold text-slate-900 font-mono">92</span>
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
                DAG Structural Integrity: 98%
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/70 text-indigo-700 text-xs font-semibold">
                <Timer className="w-3.5 h-3.5" />
                Median Cognitive Latency: 1.8s
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50/70 text-indigo-700 text-xs font-semibold">
                <Lightbulb className="w-3.5 h-3.5" />
                Epistemic Humility: High
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
              {/* Competency 1 */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">
                      1. Concept Rigor
                    </span>
                    <span className="bg-emerald-50 text-emerald-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                      Distinction
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((idx) => (
                        <div key={idx} className="w-3.5 h-1.5 rounded-full bg-indigo-600" />
                      ))}
                    </div>
                    <span className="text-xs font-bold font-mono text-slate-800">5 / 5</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Flawlessly articulated backdoor criterion and d-separation mechanics without cognitive hesitation. Maintained mathematical fidelity when mapping Pearlian do-calculus transformations.
                </p>
              </div>

              {/* Competency 2 */}
              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">
                      2. Counter-factual Reasoning
                    </span>
                    <span className="bg-indigo-50 text-indigo-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                      Strong
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4].map((idx) => (
                        <div key={idx} className="w-3.5 h-1.5 rounded-full bg-indigo-600" />
                      ))}
                      <div className="w-3.5 h-1.5 rounded-full bg-indigo-100" />
                    </div>
                    <span className="text-xs font-bold font-mono text-slate-800">4 / 5</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Constructed valid DAG counter-models when challenged by examiner on missing data mechanisms. Resolved identification bottlenecks with minor prompt intervention.
                </p>
              </div>

              {/* Competency 3 */}
              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">
                      3. Synthesis of Evidence
                    </span>
                    <span className="bg-emerald-50 text-emerald-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                      Distinction
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4, 5].map((idx) => (
                        <div key={idx} className="w-3.5 h-1.5 rounded-full bg-indigo-600" />
                      ))}
                    </div>
                    <span className="text-xs font-bold font-mono text-slate-800">5 / 5</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Synthesized quasi-experimental instrument validity with empirical bounds. Fluidly integrated synthetic controls and regression discontinuity design limits.
                </p>
              </div>

              {/* Competency 4 */}
              <div className="space-y-1.5 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900">
                      4. Dialectical Clarity
                    </span>
                    <span className="bg-slate-100 text-slate-700 text-[11px] px-2 py-0.5 rounded-full font-semibold">
                      Proficient
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      {[1, 2, 3, 4].map((idx) => (
                        <div key={idx} className="w-3.5 h-1.5 rounded-full bg-indigo-600" />
                      ))}
                      <div className="w-3.5 h-1.5 rounded-full bg-indigo-100" />
                    </div>
                    <span className="text-xs font-bold font-mono text-slate-800">4 / 5</span>
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Responded precisely under adversarial Socratic counter-probes. Re-anchored arguments back to original identification assumptions under probing stress.
                </p>
              </div>
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
                Recorded verbatim during the 45-minute live adversarial examination.
              </p>
            </div>

            <div className="space-y-4">
              {/* Dialogue Segment I */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-600" />
                    <span className="font-bold text-slate-900 font-mono text-[11px]">
                      DIALECTIC SEGMENT I &bull; MONOTONICITY BREAKDOWN
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-50 text-emerald-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                      Key Breakthrough Moment
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">18:42</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-slate-700">Dr. Julian Vance &bull; Examiner</div>
                  <p className="italic text-slate-600">
                    &ldquo;If the unobserved confounder correlates with both treatment assignment and instrumental monotonicity, why doesn't standard 2SLS preserve unbiasedness?&rdquo;
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-indigo-50/40 border border-indigo-100 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-indigo-900">Maya Lin &bull; Candidate</div>
                  <p className="text-slate-800 leading-relaxed">
                    &ldquo;Because violation of the exclusion restriction leaks structural error directly into the second stage, rendering the local average treatment effect asymptotically biased. The weights assigned to compliers become invalid when defiers exist, creating negative weighting in the estimated LATE.&rdquo;
                  </p>
                </div>
              </div>

              {/* Dialogue Segment II */}
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-600" />
                    <span className="font-bold text-slate-900 font-mono text-[11px]">
                      DIALECTIC SEGMENT II &bull; NON-PARAMETRIC BOUNDS
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-50 text-emerald-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                      Defended with Distinction
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">31:15</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50/70 border border-slate-200/80 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-slate-700">Dr. Julian Vance &bull; Examiner</div>
                  <p className="italic text-slate-600">
                    &ldquo;Propose an empirical sensitivity test if monotonicity fails.&rdquo;
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-indigo-50/40 border border-indigo-100 text-xs space-y-1">
                  <div className="text-[11px] font-bold text-indigo-900">Maya Lin &bull; Candidate</div>
                  <p className="text-slate-800 leading-relaxed">
                    &ldquo;I would apply Manski-style partial identification bounds, shifting from point estimation to sharp interval bounds. By assuming only bounded outcomes, we establish the worst-case envelope, and subsequently layer monotone instrumental variable (MIV) assumptions to shrink interval diameter without arbitrary distribution priors.&rdquo;
                  </p>
                </div>
              </div>
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
                  <span className="font-bold text-slate-900 font-mono">95%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Application</span>
                  <span className="font-bold text-slate-900 font-mono">92%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Analysis</span>
                  <span className="font-bold text-slate-900 font-mono">94%</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-50 flex items-center justify-between">
                  <span className="text-slate-500 font-medium">Evaluation</span>
                  <span className="font-bold text-slate-900 font-mono">88%</span>
                </div>
              </div>
              <div className="p-2.5 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-between text-xs">
                <span className="text-indigo-900 font-semibold">Creation &amp; Synthesis</span>
                <span className="font-bold text-indigo-700 font-mono">90% &bull; High Mastery</span>
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
                  <div className="font-bold text-slate-800">Dr. Julian Vance</div>
                  <div className="text-[10px] text-slate-400 font-mono">LEAD SOCRATIC EVALUATOR &bull; DECISION THEORY</div>
                </div>
              </div>
              <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                <span className="text-slate-500">Assessment Timestamp</span>
                <span className="font-semibold text-slate-700 font-mono">Oct 23, 2024 &bull; 14:45 UTC</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Defense Session ID</span>
                <span className="font-bold text-slate-800 font-mono">#ASY-DEF-9941</span>
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
