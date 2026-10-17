import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import {
  Sparkles,
  BookOpen,
  Mic,
  ArrowRight,
  HelpCircle,
  Send,
  CornerDownRight,
  X,
  ShieldAlert,
  CheckCircle2,
  Bookmark,
  Share2,
  ChevronLeft,
  ChevronRight,
  BrainCircuit,
  Quote,
  Lightbulb,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { ChapterDetailResponse } from '../types/api';
import { MathFormula } from '../components/atoms/MathFormula';
import { CodeSnippet } from '../components/atoms/CodeSnippet';

export const DeepReaderPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, activeChapterId } = useAppStore();

  const [chapter, setChapter] = useState<ChapterDetailResponse | null>(null);
  const [syllabusModules, setSyllabusModules] = useState<Array<{ chapter_id: string; title: string; order: number; status: string }>>([]);
  const [selectedHighlight, setSelectedHighlight] = useState<string | null>(
    'unobserved counterfactual'
  );
  const [customQuestion, setCustomQuestion] = useState('');
  const [socraticAnswer, setSocraticAnswer] = useState<string | null>(
    'Does structural invariance across observational strata logically imply the absence of latent selection bias?'
  );
  const [anchorPage, setAnchorPage] = useState<number | null>(4);
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    const sid = activeSessionId || 'sess_coding_basic';
    api.getSyllabus(sid)
      .then((res) => {
        if (res && res.chapters) {
          setSyllabusModules(res.chapters);
        }
      })
      .catch((e) => console.warn('Reader syllabus fallback:', e));
  }, [activeSessionId]);

  useEffect(() => {
    const defaultCid = activeSessionId === 'sess_coding_basic' ? 'ch_algo_01' : 'ch_01';
    const cid = activeChapterId || defaultCid;
    api.getChapter(cid)
      .then((res) => {
        setChapter(res);
      })
      .catch((e) => console.warn('Chapter fetch error fallback:', e));
  }, [activeChapterId, activeSessionId]);

  const handleAsk = async (q: string) => {
    if (!q) return;
    setIsAsking(true);
    try {
      const res = await api.socraticAsk(activeChapterId || 'ch_01', {
        session_id: activeSessionId || 'sess_a1b2c3',
        selected_text: selectedHighlight || 'statistical inference',
        question: q,
      });
      setSocraticAnswer(res.reply);
      if (res.citations && res.citations.length > 0) {
        setAnchorPage(res.citations[0].page ?? null);
      }
    } catch (err) {
      console.warn('Socratic ask error:', err);
      setSocraticAnswer(
        'If potential outcomes Y(1) and Y(0) were independent of treatment assignment conditional on covariates X, under what exact conditions could an unmeasured confounder U still induce spurious correlation?'
      );
    } finally {
      setIsAsking(false);
    }
  };

  const currentCid = activeChapterId || 'ch_01';
  const modulesList = (syllabusModules.length > 0)
    ? syllabusModules.map((m, idx) => ({
        id: m.chapter_id,
        title: `${m.order || idx + 1}. ${m.title}`,
        status: m.chapter_id === currentCid
          ? 'active'
          : (m.status === 'COMPLETED' ? 'done' : (m.status === 'LOCKED' ? 'locked' : 'ready'))
      }))
    : [
        { id: 'ch_01', title: '1. Neyman–Pearson Lemma', status: currentCid === 'ch_01' ? 'active' : 'done' },
        { id: 'ch_02', title: '2. Causal Inference & DAGs', status: currentCid === 'ch_02' ? 'active' : 'locked' },
        { id: 'ch_03', title: '3. Epistemology of AI Reason', status: currentCid === 'ch_03' ? 'active' : 'locked' },
        { id: 'ch_04', title: '4. Kolmogorov Descriptive Bounds', status: currentCid === 'ch_04' ? 'active' : 'locked' },
      ];

  const currentModuleIdx = modulesList.findIndex((m) => m.id === currentCid);
  const displayModuleNumber = currentModuleIdx >= 0 ? currentModuleIdx + 1 : 1;

  return (
    <div className="space-y-6 animate-in fade-in duration-200 pb-12">
      {/* Top Session Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-primary-600 font-mono">
              Inquiry Workspace &bull; Track 04
            </span>
            <Badge variant="success" size="sm" hasDot>
              Session Active
            </Badge>
          </div>
          <h1 className="text-lg font-bold text-slate-900">
            {chapter?.title ? `Dialectic Epistemology: ${chapter.title}` : 'Dialectic Epistemology & Inference: Neyman–Pearson Foundations'}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/app/roadmap')}
            leftIcon={<ChevronLeft className="w-4 h-4" />}
          >
            Roadmap
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/app/exam')}
            leftIcon={<Mic className="w-4 h-4" />}
          >
            Start Oral Defense
          </Button>
        </div>
      </div>

      {/* 3-Column Split Reading Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Chapters & Modules Stepper (3 Cols) */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="p-4 space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-900">
              <span>Curriculum Modules</span>
              <span className="text-primary-600 font-mono text-[11px]">
                {displayModuleNumber} of {modulesList.length}
              </span>
            </div>

            <div className="space-y-1.5">
              {modulesList.map((mod) => (
                <div
                  key={mod.id}
                  onClick={() => {
                    useAppStore.getState().setActiveChapterId(mod.id);
                  }}
                  className={`p-2.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors cursor-pointer ${
                    mod.status === 'active'
                      ? 'bg-primary-50 text-primary-700 border border-primary-200/80 shadow-xs'
                      : mod.status === 'done'
                      ? 'text-slate-700 hover:bg-slate-50'
                      : 'text-slate-400 opacity-60 hover:opacity-100 hover:bg-slate-50'
                  }`}
                >
                  <span className="truncate">{mod.title}</span>
                  {mod.status === 'done' && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  )}
                  {mod.status === 'active' && (
                    <span className="w-2 h-2 rounded-full bg-primary-600 animate-pulse shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Interactive Hint */}
          <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-100 text-xs text-primary-900 space-y-1.5">
            <div className="flex items-center gap-1.5 font-bold text-primary-700">
              <Lightbulb className="w-4 h-4 text-primary-600" />
              <span>Socratic Dialectic Mode</span>
            </div>
            <p className="leading-relaxed text-slate-600 text-[11px]">
              Click on any <span className="font-semibold text-primary-700 bg-white px-1 py-0.5 rounded border border-primary-200">highlighted term</span> to prompt the examiner for an adversarial counter-thesis.
            </p>
          </div>
        </div>

        {/* Center Column: Reading Paper / Deep Reader Text (6 Cols) */}
        <div className="lg:col-span-6 space-y-4">
          <Card className="p-7 space-y-6 bg-white shadow-card">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 text-xs text-slate-400">
              <span>Section 3.2 &bull; Likelihood Ratio Foundations</span>
              <span>Paragraph 4 of 18</span>
            </div>

            {/* Reading Content */}
            <article className="prose max-w-none text-slate-800 text-sm leading-relaxed space-y-4">
              <h2 className="text-xl font-extrabold text-slate-900">
                {chapter?.title || 'The Fundamental Lemma of Hypothesis Testing'}
              </h2>

              {currentCid !== 'ch_01' ? (
                <div className="space-y-4 text-slate-800 text-sm leading-relaxed">
                  <div className="p-4 rounded-xl bg-indigo-50/50 border border-indigo-100 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-indigo-900">Module Status: {chapter?.status || 'LOCKED'}</span>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Reading time: {chapter?.estimated_reading_minutes || 15} minutes &bull; Source pages: {chapter?.source_pages?.join(', ') || '1, 2'}
                      </p>
                    </div>
                    {chapter?.interview_available && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => navigate('/app/exam')}
                        leftIcon={<Mic className="w-3.5 h-3.5" />}
                      >
                        Enter Defense
                      </Button>
                    )}
                  </div>

                  {chapter?.content_markdown ? (
                    chapter.content_markdown
                      .split('\n\n')
                      .filter((p) => !p.trim().startsWith('#'))
                      .map((p, idx) => (
                        <p key={idx} className="leading-relaxed">
                          {p.includes(':') ? (
                            <>
                              {p.split(':')[0]}:{' '}
                              <span
                                onClick={() => {
                                  const term = p.split(':')[0].trim();
                                  setSelectedHighlight(term);
                                  handleAsk(`What is the core fallacy or boundary condition regarding ${term}?`);
                                }}
                                className="socratic-highlight cursor-pointer"
                              >
                                {p.split(':')[1]}
                              </span>
                            </>
                          ) : (
                            p
                          )}
                        </p>
                      ))
                  ) : (
                    <p className="text-slate-500 italic">
                      Chapter content is locked pending Socratic validation of prior module.
                    </p>
                  )}
                </div>
              ) : (
                <>
                  <p>
                    In standard decision theoretic protocols, the central paradox of empirical observation resides in the{' '}
                    <span
                      onClick={() => {
                        setSelectedHighlight('unobserved counterfactual');
                        setSocraticAnswer(
                          'Does structural invariance across observational strata logically imply the absence of latent selection bias?'
                        );
                      }}
                      className="socratic-highlight"
                    >
                      unobserved counterfactual
                    </span>
                    : what would have transpired had the treatment not been assigned? In standard randomized controlled protocols, balance secures exchangeability in expectation.
                  </p>

                  <p>
                    However, when comparing simple hypotheses <MathFormula math="H_0: \theta = \theta_0" /> versus <MathFormula math="H_1: \theta = \theta_1" />, the{' '}
                    <span
                      onClick={() => {
                        setSelectedHighlight('Neyman-Pearson lemma');
                        setSocraticAnswer(
                          'If the probability density ratio is non-monotonic, can a Uniformly Most Powerful (UMP) test still be constructed?'
                        );
                      }}
                      className="socratic-highlight"
                    >
                      Neyman-Pearson lemma
                    </span>{' '}
                    demonstrates that the likelihood ratio test statistic <MathFormula math="\Lambda(x) = \frac{L(\theta_0 \mid x)}{L(\theta_1 \mid x)}" /> is mathematically optimal. It achieves maximum statistical power while strictly bounding the Type I error rate at significance level <MathFormula math="\alpha" />.
                  </p>

                  <blockquote className="border-l-4 border-l-primary-500 pl-4 py-2 my-4 bg-slate-50 rounded-r-lg text-slate-800 text-xs leading-relaxed">
                    <span className="italic font-serif">&ldquo;For any test of size <MathFormula math="\alpha" />, the test with critical region <MathFormula math="W = \{x \mid \frac{f(x \mid \theta_1)}{f(x \mid \theta_0)} > k\}" /> maximizes the power <MathFormula math="1 - \beta" />.&rdquo;</span>
                  </blockquote>

                  <p>
                    Sample independence guarantees that the composite random vector produces a product measure over the sample space. Under classical regularity conditions, when observations <MathFormula math="X_1, \dots, X_n" /> are drawn independently from parameterized distribution <MathFormula math="f(x; \theta)" />, the joint likelihood factors cleanly, guaranteeing the monotone likelihood ratio property holds uniformly.
                  </p>
                </>
              )}

              {/* Contextual Visual: Algorithm Complexity for Coding Track vs Statistical Partition for Math Track */}
              {activeSessionId === 'sess_coding_basic' || chapter?.chapter_id?.includes('algo') ? (
                <div className="my-6 p-6 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-4 flex flex-col items-center">
                  {/* KaTeX Asymptotic Bound Card */}
                  <div className="bg-white border border-slate-200 rounded-xl px-8 py-3.5 shadow-xs text-center">
                    <MathFormula
                      math="f(n) \in \mathcal{O}(g(n)) \iff \exists c > 0, n_0 > 0 : 0 \le f(n) \le c \cdot g(n) \quad \forall n \ge n_0"
                      className="text-sm md:text-base bg-transparent border-none shadow-none font-serif tracking-wide"
                    />
                  </div>

                  {/* Asymptotic Growth Curves SVG (Figure 1.1) */}
                  <div className="w-full max-w-md bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs space-y-2">
                    <svg viewBox="0 0 400 130" className="w-full h-auto overflow-visible select-none">
                      {/* Axes */}
                      <line x1="30" y1="110" x2="380" y2="110" stroke="#cbd5e1" strokeWidth="1.5" />
                      <line x1="30" y1="110" x2="30" y2="10" stroke="#cbd5e1" strokeWidth="1.5" />
                      
                      {/* Curve 1: O(1) Constant */}
                      <line x1="30" y1="100" x2="370" y2="100" stroke="#10b981" strokeWidth="2" />
                      <text x="375" y="103" fill="#10b981" fontSize="9" fontWeight="bold">O(1)</text>

                      {/* Curve 2: O(log n) Logarithmic */}
                      <path d="M 30,105 Q 120,75 370,68" fill="none" stroke="#06b6d4" strokeWidth="2" />
                      <text x="375" y="70" fill="#06b6d4" fontSize="9" fontWeight="bold">O(log n)</text>

                      {/* Curve 3: O(n) Linear */}
                      <line x1="30" y1="110" x2="350" y2="35" stroke="#4f46e5" strokeWidth="2" />
                      <text x="355" y="38" fill="#4f46e5" fontSize="9" fontWeight="bold">O(n)</text>

                      {/* Curve 4: O(n^2) Quadratic */}
                      <path d="M 30,110 Q 150,95 240,15" fill="none" stroke="#f43f5e" strokeWidth="2" strokeDasharray="3 3" />
                      <text x="245" y="18" fill="#f43f5e" fontSize="9" fontWeight="bold">O(n²)</text>
                    </svg>

                    <p className="text-center text-[10px] text-slate-500 font-medium leading-relaxed">
                      <strong className="text-slate-800">Figure 1.1:</strong> Asymptotic growth frontiers illustrating constant, logarithmic, linear, and polynomial resource scaling.
                    </p>
                  </div>

                  {/* Interactive Code Implementation Block */}
                  <div className="w-full">
                    <CodeSnippet
                      block={true}
                      language="python"
                      filename="binary_search_invariant.py"
                      code={`def binary_search(arr: list[int], target: int) -> int:
    """O(log n) logarithmic search over sorted sequence."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1`}
                    />
                  </div>
                </div>
              ) : (
                <div className="my-6 p-6 rounded-2xl bg-slate-50/80 border border-slate-200/80 space-y-4 flex flex-col items-center">
                  {/* White floating formula card rendered via KaTeX */}
                  <div className="bg-white border border-slate-200 rounded-xl px-8 py-3.5 shadow-xs text-center">
                    <MathFormula
                      math="\Lambda(x) = \frac{L(\theta_0 \mid x)}{L(\theta_1 \mid x)} \le k"
                      className="text-base md:text-lg bg-transparent border-none shadow-none font-serif tracking-wide"
                    />
                  </div>

                  {/* Partition diagram SVG (Figure 3.1) */}
                  <div className="w-full max-w-md bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs space-y-2">
                    <svg viewBox="0 0 400 120" className="w-full h-auto overflow-visible select-none">
                      {/* Baseline */}
                      <line x1="20" y1="100" x2="380" y2="100" stroke="#cbd5e1" strokeWidth="1.5" />
                      
                      {/* Curve 1: Null distribution f(x | θ0) */}
                      <path
                        d="M 30,100 C 70,100 100,20 150,20 C 200,20 230,100 270,100"
                        fill="rgba(79, 70, 229, 0.08)"
                        stroke="#4f46e5"
                        strokeWidth="2"
                      />
                      {/* Curve 2: Alt distribution f(x | θ1) */}
                      <path
                        d="M 140,100 C 180,100 210,35 260,35 C 310,35 340,100 370,100"
                        fill="rgba(14, 165, 233, 0.08)"
                        stroke="#0284c7"
                        strokeWidth="2"
                      />
                      
                      {/* Threshold line k */}
                      <line x1="230" y1="10" x2="230" y2="100" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 4" />
                      <text x="235" y="18" fill="#d97706" fontSize="10" fontWeight="bold" fontFamily="sans-serif">
                        threshold k
                      </text>

                      {/* Region labels */}
                      <text x="80" y="90" fill="#64748b" fontSize="9" fontWeight="600" fontFamily="sans-serif">
                        Region R(1)
                      </text>
                      <text x="250" y="90" fill="#4f46e5" fontSize="9" fontWeight="bold" fontFamily="sans-serif">
                        Region R (Rejection)
                      </text>
                    </svg>

                    <p className="text-center text-[10px] text-slate-500 font-medium leading-relaxed">
                      <strong className="text-slate-800">Figure 3.1:</strong> Partitioning the sample space into rejection region R and acceptance region Rᶜ based on threshold k.
                    </p>
                  </div>
                </div>
              )}

              <p>
                In regulatory clinical trial design, this duality dictates the required sample allocation. When testing non-inferiority margins, controlling &alpha; protects against approving ineffective interventions, while bounding &beta; guards trial sponsors against premature termination of therapeutically viable molecules.
              </p>

              {/* Algorithmic Code Implementation Example Section */}
              <div className="pt-4 space-y-3 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-indigo-600" />
                    Computational Implementation: Vectorized LRT
                  </h3>
                  <span className="text-[11px] font-mono text-slate-400">Python 3.11 &bull; NumPy</span>
                </div>
                
                <p className="text-xs text-slate-600 leading-relaxed">
                  Below is the vectorized implementation of the Neyman-Pearson likelihood ratio decision boundary for Gaussian mean shift testing (<MathFormula math="\theta_0 \to \theta_1" />). Notice how the critical threshold <CodeSnippet code="k_threshold" /> is computed strictly under the null hypothesis quantile:
                </p>

                <CodeSnippet
                  filename="neyman_pearson_lrt.py"
                  language="python"
                  block
                  code={`import numpy as np

def neyman_pearson_lrt(
    x: np.ndarray, 
    theta_0: float = 0.0, 
    theta_1: float = 1.0, 
    alpha: float = 0.05
) -> dict:
    """
    Uniformly Most Powerful (UMP) Neyman-Pearson Test
    H0: theta = theta_0 vs H1: theta = theta_1 (known sigma = 1.0)
    """
    n = len(x)
    
    # 1. Compute Log-Likelihood Ratio test statistic
    # Lambda(x) = (theta_1 - theta_0) * sum(x) - 0.5 * n * (theta_1^2 - theta_0^2)
    log_lambda = (theta_1 - theta_0) * np.sum(x) - 0.5 * n * (theta_1**2 - theta_0**2)
    
    # 2. Derive exact threshold k from significance level alpha
    z_crit = 1.644853  # Phi^-1(1 - alpha) for alpha = 0.05
    k_threshold = (theta_1 - theta_0) * (n * theta_0 + np.sqrt(n) * z_crit) - 0.5 * n * (theta_1**2 - theta_0**2)
    
    # 3. Decision Rule: Reject H0 if log_lambda > k_threshold
    reject_null = bool(log_lambda > k_threshold)
    
    return {
        "test_statistic": round(float(log_lambda), 4),
        "critical_threshold": round(float(k_threshold), 4),
        "verdict": "REJECT_H0 (Optimal Defense)" if reject_null else "FAIL_TO_REJECT_H0"
    }`}
                />

                <p className="text-xs text-slate-500 leading-relaxed">
                  In practice, the test statistic <CodeSnippet code="log_lambda" /> is evaluated in <MathFormula math="\mathcal{O}(N)" /> time complexity, making the decision boundary computationally efficient even for streaming observational telemetry.
                </p>
              </div>
            </article>

            {/* In-Line Socratic Popover Box */}
            {selectedHighlight && (
              <div className="mt-6 p-5 rounded-2xl bg-gradient-to-b from-primary-50/80 to-white border border-primary-200/90 shadow-hover space-y-4 animate-in fade-in zoom-in-95 duration-150">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-primary-600 text-white flex items-center justify-center">
                      <BrainCircuit className="w-4 h-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900">
                        Active Socratic Prompt
                      </div>
                      <div className="text-[10px] text-primary-700 font-mono">
                        Target Concept: "{selectedHighlight}"
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedHighlight(null)}
                    className="text-slate-400 hover:text-slate-600 p-1"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Socratic Counter-Question */}
                {socraticAnswer && (
                  <div className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs space-y-2">
                    <p className="text-xs font-semibold text-slate-900 italic leading-relaxed">
                      &ldquo;{socraticAnswer}&rdquo;
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-100">
                      <span>Adversarial Probe &bull; Bloom L5</span>
                      <span className="text-emerald-600 font-semibold">Gave Direct Answer: False</span>
                    </div>
                  </div>
                )}

                {/* Quick Action Buttons */}
                <div className="flex flex-wrap items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs text-primary-700 border-primary-200 bg-white hover:bg-primary-50"
                    onClick={() =>
                      handleAsk(
                        'Does structural invariance prevent selection bias?'
                      )
                    }
                  >
                    Formulate Counter-Thesis
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs text-slate-700 border-slate-200 bg-white hover:bg-slate-50"
                    onClick={() =>
                      handleAsk(
                        'Cite contextual evidence from page 4'
                      )
                    }
                  >
                    Cite Contextual Evidence
                  </Button>
                </div>

                {/* Interactive Inquiry Input */}
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={customQuestion}
                    onChange={(e) => setCustomQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAsk(customQuestion)}
                    placeholder="Enter your response or counter-proof..."
                    className="flex-1 bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  />
                  <Button
                    size="sm"
                    variant="primary"
                    isLoading={isAsking}
                    onClick={() => handleAsk(customQuestion)}
                    rightIcon={<Send className="w-3.5 h-3.5" />}
                  >
                    Interrogate
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: Dialectic Progress & Dossier Readiness (3 Cols) */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="p-5 space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-900">Dialectic Progress</span>
              <Badge variant="primary" size="sm">Score 92%</Badge>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Falsifiability Index</span>
                  <span className="font-bold text-slate-800 font-mono">0.88</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-primary-600 h-1.5 rounded-full" style={{ width: '88%' }} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Dialectic Depth Tier</span>
                  <span className="font-bold text-primary-600">Mastery IV</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: '80%' }} />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Verified Citations</span>
                  <span className="font-bold text-slate-800 font-mono">14 Nodes</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: '95%' }} />
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 space-y-2">
              <Button
                variant="primary"
                size="md"
                className="w-full"
                onClick={() => navigate('/app/exam')}
                leftIcon={<Mic className="w-4 h-4" />}
              >
                Defend in Oral Exam
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs text-slate-600"
                onClick={() => navigate('/app/report')}
              >
                View Cumulative Dossier
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
