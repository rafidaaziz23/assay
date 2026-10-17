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

export const DeepReaderPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, activeChapterId } = useAppStore();

  const [chapter, setChapter] = useState<ChapterDetailResponse | null>(null);
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
    const cid = activeChapterId || 'ch_01';
    api.getChapter(cid)
      .then((res) => {
        setChapter(res);
      })
      .catch((e) => console.warn('Chapter fetch error fallback:', e));
  }, [activeChapterId]);

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
            Dialectic Epistemology & Inference: Neyman–Pearson Foundations
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
              <span className="text-primary-600 font-mono text-[11px]">3 of 6</span>
            </div>

            <div className="space-y-1.5">
              {[
                { id: '1', title: '1. Probability Spaces', status: 'done' },
                { id: '2', title: '2. Point Estimation', status: 'done' },
                { id: '3', title: '3. Neyman–Pearson Lemma', status: 'active' },
                { id: '4', title: '4. Uniformly Most Powerful Tests', status: 'locked' },
                { id: '5', title: '5. Likelihood Ratio Tests', status: 'locked' },
              ].map((mod) => (
                <div
                  key={mod.id}
                  className={`p-2.5 rounded-lg text-xs font-semibold flex items-center justify-between transition-colors cursor-pointer ${
                    mod.status === 'active'
                      ? 'bg-primary-50 text-primary-700 border border-primary-200/80 shadow-xs'
                      : mod.status === 'done'
                      ? 'text-slate-700 hover:bg-slate-50'
                      : 'text-slate-400 opacity-60'
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
                The Fundamental Lemma of Hypothesis Testing
              </h2>

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
                However, when comparing simple hypotheses H<sub>0</sub>: &theta; = &theta;<sub>0</sub> versus H<sub>1</sub>: &theta; = &theta;<sub>1</sub>, the{' '}
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
                demonstrates that the likelihood ratio test statistic &Lambda;(x) = L(&theta;<sub>0</sub> | x) / L(&theta;<sub>1</sub> | x) is mathematically optimal. It achieves maximum statistical power while strictly bounding the Type I error rate at significance level &alpha;.
              </p>

              <blockquote className="border-l-4 border-l-primary-500 pl-4 py-1 my-4 bg-slate-50 rounded-r-lg text-slate-700 italic text-xs leading-relaxed">
                &ldquo;For any test of size &alpha;, the test with critical region W = &#123;x | f(x | &theta;<sub>1</sub>) / f(x | &theta;<sub>0</sub>) &gt; k&#125; maximizes the power 1 &minus; &beta;.&rdquo;
              </blockquote>

              <p>
                Notice how the critical value $k$ is determined strictly by the null distribution. Any departure from the monotone likelihood ratio property destroys the uniform optimality across compound alternate parameter spaces.
              </p>
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
