import React, { useState, useEffect, useRef } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Avatar } from '../components/atoms/Avatar';
import {
  Mic,
  MicOff,
  Sparkles,
  Send,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  Award,
  ArrowRight,
  BrainCircuit,
  Volume2,
  RotateCcw,
  Sliders,
  Check,
  Square,
  Unlock,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { useVoiceDefense } from '../hooks/useVoiceDefense';
import { InterviewStartResponse } from '../types/api';

export const ExamPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId, activeChapterId, setActiveChapterId, activeTrack, user } = useAppStore();

  const [examState, setExamState] = useState<'inquiry' | 'calibration' | 'verdict'>('inquiry');
  const [turnIndex, setTurnIndex] = useState(1);
  const [confidenceScore, setConfidenceScore] = useState(85);
  const [actualScore, setActualScore] = useState(94);
  const [interviewData, setInterviewData] = useState<InterviewStartResponse | null>(null);

  const [chatLog, setChatLog] = useState<
    Array<{
      sender: 'examiner' | 'candidate';
      text: string;
      isFallacyTrap?: boolean;
    }>
  >([]);

  const [candidateInput, setCandidateInput] = useState('');

  // Voice hook integration
  const {
    isListening,
    transcript,
    waveformBars,
    stopListening,
    toggleListening,
  } = useVoiceDefense((spoken) => {
    if (spoken && spoken.trim()) {
      setCandidateInput(spoken);
    }
  });

  const speakExaminer = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  useEffect(() => {
    const defaultCid = activeSessionId === 'sess_coding_basic' ? 'ch_algo_01' : (activeSessionId === 'sess_dist_systems' ? 'ch_dist_01' : 'ch_01');
    const cid = activeChapterId || defaultCid;
    const sid = activeSessionId || 'sess_coding_basic';

    api.startInterview(cid, sid)
      .then((res) => {
        setInterviewData(res);
        if (res.first_question) {
          setChatLog([
            {
              sender: 'examiner',
              text: res.first_question,
            },
          ]);
        }
      })
      .catch((e) => {
        console.warn('Interview start fallback:', e);
        const candidateName = user?.name || 'Rafida Aziz';
        const fallbackQ =
          activeTrack === 'coding'
            ? `Candidate ${candidateName}. In basic algorithm complexity, explain how the 'Constant-Time Binary Filter' allows binary search to achieve O(1) lookups on an unsorted array without preprocessing.`
            : (activeTrack === 'distributed'
              ? `Candidate ${candidateName}. In designing a distributed datastore, an architect claims that by eliminating leader election and utilizing deterministic quorum broadcast, the system achieves 100% liveness and safety during network partitions without unbounded wait. Does this violate the FLP theorem?`
              : `Candidate ${candidateName}. In evaluating the Neyman-Pearson lemma, suppose an analyst claims that increasing the significance level alpha from 0.05 to 0.10 will simultaneously reduce Type II error beta and widen the critical region. Is this logically consistent, or does an unstated trade-off exist?`);
        setChatLog([
          {
            sender: 'examiner',
            text: fallbackQ,
          },
        ]);
      });
  }, [activeChapterId, activeSessionId, activeTrack, user]);

  const handleSendResponse = async (textToSend?: string) => {
    stopListening();
    const val = textToSend || candidateInput;
    if (!val.trim()) return;

    const updated = [
      ...chatLog,
      { sender: 'candidate' as const, text: val },
    ];
    setChatLog(updated);
    setCandidateInput('');

    const cid = activeChapterId || 'ch_01';
    const interviewId = interviewData?.interview_id || 'intv_demo_01';

    try {
      if (turnIndex === 1) {
        setTurnIndex(2);
        const turnRes = await api.interviewTurn(cid, {
          interview_id: interviewId,
          turn_index: 1,
          user_response: val,
        });

        setChatLog([
          ...updated,
          {
            sender: 'examiner',
            text: turnRes.interrogator_response || 'Correct point regarding the size of the critical region. Now consider an adversarial probe: If the distribution fails the monotone likelihood ratio condition, can we still assert that the Neyman-Pearson critical test is Uniformly Most Powerful (UMP) across all composite alternatives?',
            isFallacyTrap: turnRes.honeypot_active,
          },
        ]);
      } else {
        // Advanced to calibration phase
        setExamState('calibration');
      }
    } catch (err) {
      console.warn('Turn error fallback:', err);
      setExamState('calibration');
    }
  };

  const handleSubmitVoice = () => {
    stopListening();
    const val = candidateInput.trim();
    if (!val) {
      return;
    }
    handleSendResponse(val);
  };

  const handleCompleteDefense = async () => {
    const cid = activeChapterId || 'ch_01';
    const interviewId = interviewData?.interview_id || 'intv_demo_01';

    try {
      await api.submitCalibration(cid, interviewId, confidenceScore);
      const finalRes = await api.finalizeInterview(
        cid,
        interviewId,
        chatLog[chatLog.length - 1]?.text || 'Final reasoning submitted.'
      );
      if (finalRes.score?.chapter_score) {
        setActualScore(finalRes.score.chapter_score);
      }
    } catch (e) {
      console.warn('Finalize error fallback:', e);
    }
    setExamState('verdict');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in duration-200 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-purple-100 border border-purple-200 text-purple-700 flex items-center justify-center font-bold">
            <Mic className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 font-mono">
                Oral Defense Chamber &bull; Rigor L5
              </span>
              <Badge variant="purple" size="sm" hasDot>
                Live Vocal Defense
              </Badge>
            </div>
            <h1 className="text-lg font-bold text-slate-900">
              Module Capstone: {
                interviewData?.chapter_title ||
                (activeTrack === 'coding'
                  ? 'Algorithmic Complexity & Asymptotic Bounds'
                  : (activeTrack === 'distributed'
                    ? 'State Machine Replication & FLP Impossibility'
                    : 'Neyman–Pearson LRT & Error Bounds'))
              }
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-bold text-slate-900">
              {activeTrack === 'distributed' ? 'Prof. Elena Rostova' : 'Assay AI'}
            </div>
            <div className="text-[10px] text-slate-400">
              {activeTrack === 'distributed' ? 'Principal Scientist · Distributed Systems' : 'Lead Socratic AI Evaluator · Algorithms'}
            </div>
          </div>
          <Avatar
            name={activeTrack === 'distributed' ? 'Elena Rostova' : 'Assay AI'}
            size="md"
          />
        </div>
      </div>

      {/* Main Defense Flow */}
      {examState === 'inquiry' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left/Center: Dialogue Transcript (2 Cols) */}
          <div className="lg:col-span-2 space-y-4">
            <Card className="p-6 space-y-4 min-h-[420px] flex flex-col justify-between bg-white shadow-card">
              {/* Dialogue Log */}
              <div className="space-y-4 overflow-y-auto max-h-[380px] pr-2">
                {chatLog.map((item, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col ${
                      item.sender === 'candidate' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[11px] font-bold text-slate-500">
                        {item.sender === 'examiner'
                          ? (activeTrack === 'distributed' ? 'Prof. Elena Rostova (Examiner)' : 'Assay AI (Examiner)')
                          : `${user?.name || 'Rafida Aziz'} (Candidate)`}
                      </span>
                      {item.sender === 'examiner' && (
                        <button
                          type="button"
                          onClick={() => speakExaminer(item.text)}
                          className="p-1 rounded-md text-slate-400 hover:text-indigo-600 hover:bg-slate-100 transition-colors cursor-pointer"
                          title="Listen to examiner voice"
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                      {item.isFallacyTrap && (
                        <Badge variant="warning" size="sm">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Adversarial Fallacy Probe
                        </Badge>
                      )}
                    </div>
                    <div
                      className={`p-4 rounded-2xl max-w-[85%] text-xs leading-relaxed ${
                        item.sender === 'candidate'
                          ? 'bg-primary-600 text-white rounded-tr-xs'
                          : 'bg-slate-50 border border-slate-200/80 text-slate-900 rounded-tl-xs shadow-xs'
                      }`}
                    >
                      {item.text}
                    </div>
                  </div>
                ))}
              </div>

              {/* Interactive Audio Waveform & Input Tray */}
              <div className="pt-4 border-t border-slate-100 space-y-3">
                {/* Waveform Visualizer & Live Voice Tray */}
                <div
                  className={`p-3 sm:p-3.5 rounded-xl transition-all duration-200 overflow-hidden ${
                    isListening
                      ? 'bg-slate-900 ring-2 ring-indigo-500/50 shadow-md text-white'
                      : 'bg-slate-900 text-white'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <button
                        type="button"
                        onClick={toggleListening}
                        className={`w-9 h-9 sm:w-10 sm:h-10 shrink-0 rounded-full flex items-center justify-center transition-all cursor-pointer ${
                          isListening
                            ? 'bg-rose-500 hover:bg-rose-600 text-white ring-4 ring-rose-500/30'
                            : 'bg-primary-600 hover:bg-primary-700 text-white'
                        }`}
                        title={isListening ? 'Klik untuk mematikan mikrofon' : 'Klik untuk menyalakan mikrofon'}
                      >
                        {isListening ? (
                          <MicOff className="w-4 h-4 sm:w-5 sm:h-5" />
                        ) : (
                          <Mic className="w-4 h-4 sm:w-5 sm:h-5" />
                        )}
                      </button>
                      <div className="min-w-0">
                        <div className="text-xs font-bold flex items-center gap-1.5 truncate">
                          <span className="truncate">{isListening ? 'Mendengarkan...' : 'Mikrofon Siap'}</span>
                          {isListening && (
                            <span className="shrink-0 w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono truncate">
                          {isListening ? 'Bicara sekarang' : 'Klik mic untuk berbicara lisan'}
                        </div>
                      </div>
                    </div>

                    {/* Animated Bars */}
                    <div className="flex items-center gap-0.5 sm:gap-1 h-6 sm:h-8 px-1 flex-1 max-w-[130px] sm:max-w-[160px] justify-center overflow-hidden">
                      {waveformBars.slice(0, 16).map((height, i) => (
                        <div
                          key={i}
                          className={`w-0.5 sm:w-1 rounded-full transition-all duration-75 shrink-0 ${
                            isListening ? 'bg-primary-400' : 'bg-slate-700'
                          }`}
                          style={{ height: `${height}%` }}
                        />
                      ))}
                    </div>

                    {/* Clean Compact Icon Buttons when Listening */}
                    {isListening && (
                      <div className="flex items-center gap-1.5 shrink-0">
                        {/* Stop Icon Button */}
                        <button
                          type="button"
                          onClick={stopListening}
                          className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-rose-950/60 text-slate-300 hover:text-rose-400 border border-slate-700 hover:border-rose-500/50 flex items-center justify-center transition-all cursor-pointer shadow-xs"
                          title="Hentikan Mikrofon"
                          aria-label="Hentikan"
                        >
                          <Square className="w-3.5 h-3.5 fill-current" />
                        </button>

                        {/* Send Icon Button */}
                        <button
                          type="button"
                          onClick={handleSubmitVoice}
                          disabled={!candidateInput.trim()}
                          className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all cursor-pointer shadow-xs ${
                            candidateInput.trim()
                              ? 'bg-emerald-500 hover:bg-emerald-600 text-white'
                              : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed opacity-50'
                          }`}
                          title={candidateInput.trim() ? 'Kirim Jawaban' : 'Ketik atau bicara untuk mengisi jawaban'}
                          aria-label="Kirim"
                        >
                          <Send className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Live speech preview pill */}
                  {isListening && (
                    <div className="mt-2.5 pt-2.5 border-t border-slate-800/80 flex items-center justify-between gap-2 text-xs">
                      <div className="flex items-center gap-2 truncate text-slate-300">
                        <span className="text-slate-400 font-mono text-[10px] uppercase tracking-wider shrink-0">Transkrip:</span>
                        <span className="text-primary-200 font-medium italic truncate">
                          {candidateInput.trim() ? `"${candidateInput}"` : '(Mendengarkan... silakan bicara ke mikrofon atau ketik teks di bawah)'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Quick candidate response options */}
                <div className="flex flex-wrap items-center gap-2">
                  {activeTrack === 'coding' ? (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs text-indigo-700 border-indigo-200 bg-indigo-50/60 hover:bg-indigo-100 font-medium"
                        onClick={() =>
                          handleSendResponse(
                            'That concept is completely fictional. Binary search requires a sorted array to halve the search space each step (O(log n)). On an unsorted array, you must scan linearly in O(n) time.'
                          )
                        }
                      >
                        Expose Binary Filter Fallacy (Recommended)
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs text-slate-700 hover:bg-slate-100"
                        onClick={() =>
                          handleSendResponse(
                            'Binary search operates via the recurrence T(n) = T(n/2) + O(1), which solves to O(log n) by the Master Theorem. Unsorted lookups strictly require Ω(n) comparisons.'
                          )
                        }
                      >
                        Recurrence Derivation
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs text-slate-700"
                        onClick={() =>
                          handleSendResponse(
                            'It is logically consistent. Expanding alpha expands the rejection boundary W, reducing Type II error beta and increasing test power 1 - beta.'
                          )
                        }
                      >
                        Argue Rejection Boundary Trade-off
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs text-slate-700"
                        onClick={() =>
                          handleSendResponse(
                            'No, without the monotone likelihood ratio property, the Karlin-Rubin theorem fails and the test ceases to be UMP.'
                          )
                        }
                      >
                        Expose Karlin-Rubin Invalidation
                      </Button>
                    </>
                  )}
                </div>

                {/* Text input backup */}
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={candidateInput}
                    onChange={(e) => setCandidateInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSendResponse()}
                    placeholder="State your formal defense or counter-proof..."
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                  />
                  <Button
                    variant="primary"
                    size="md"
                    onClick={() => handleSendResponse()}
                    rightIcon={<Send className="w-4 h-4" />}
                  >
                    Submit Defense
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column: Live Rubric & Socratic Meter (1 Col) */}
          <div className="space-y-4">
            <Card className="p-5 space-y-4 bg-white">
              <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                <span>Rubric Competencies</span>
                <Badge variant="primary" size="sm">4 Evaluated</Badge>
              </div>

              <div className="space-y-3.5">
                {[
                  {
                    name: 'First-Principles Derivation',
                    score: 94,
                    status: 'Exceeded',
                    variant: 'success' as const,
                  },
                  {
                    name: 'Boundary Resilience',
                    score: 88,
                    status: 'Certified',
                    variant: 'primary' as const,
                  },
                  {
                    name: 'Fallacy Detection',
                    score: 92,
                    status: 'Certified',
                    variant: 'success' as const,
                  },
                  {
                    name: 'Anti-Hallucination Grounding',
                    score: 96,
                    status: 'Exceeded',
                    variant: 'success' as const,
                  },
                ].map((crit) => (
                  <div key={crit.name} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-medium text-slate-700">{crit.name}</span>
                      <span className="font-bold font-mono text-slate-900">
                        {crit.score}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-primary-600 h-1.5 rounded-full"
                        style={{ width: `${crit.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-3 border-t border-slate-100 text-xs text-slate-500 space-y-2">
                <div className="flex items-center gap-1.5 text-emerald-600 font-semibold">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Zero logical fallacies accepted</span>
                </div>
                <p className="text-[11px] leading-relaxed text-slate-400">
                  Examiner is evaluating causal depth, counterfactual synthesis, and refusal of ungrounded leaps.
                </p>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Calibration Phase */}
      {examState === 'calibration' && (
        <Card className="p-8 max-w-2xl mx-auto space-y-6 text-center animate-in zoom-in-95 duration-200">
          <div className="w-12 h-12 rounded-2xl bg-primary-50 text-primary-600 border border-primary-200 flex items-center justify-center mx-auto">
            <Sliders className="w-6 h-6" />
          </div>

          <div className="space-y-2">
            <h2 className="text-xl font-bold text-slate-900">
              Calibrate Your Socratic Confidence
            </h2>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Before the grand jury reveals your certified evaluation, predict your mastery level to calibrate your metacognitive accuracy.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-4">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-slate-500">Predicted Rigor Score</span>
              <span className="text-2xl font-mono text-primary-600 font-extrabold">
                {confidenceScore}%
              </span>
            </div>

            <input
              type="range"
              min="50"
              max="100"
              value={confidenceScore}
              onChange={(e) => setConfidenceScore(Number(e.target.value))}
              className="w-full accent-primary-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
            />

            <div className="flex justify-between text-[11px] text-slate-400 font-mono">
              <span>50% (Tentative)</span>
              <span>75% (Applied)</span>
              <span>100% (First-Principles)</span>
            </div>
          </div>

          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={handleCompleteDefense}
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Finalize Defense & Reveal Dossier
          </Button>
        </Card>
      )}

      {/* Verdict / Passed Phase */}
      {examState === 'verdict' && (
        <Card className="p-8 max-w-2xl mx-auto space-y-6 text-center animate-in zoom-in-95 duration-200">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-md shadow-emerald-600/20">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-700">
              <Award className="w-4 h-4" />
              Oral Defense Passed with Distinction
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900">
              {activeTrack === 'coding' ? 'Module 01 Certified: 92% Dialectic Rigor' : 'Module 03 Certified: 94% Dialectic Rigor'}
            </h2>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              {activeTrack === 'coding'
                ? 'You successfully deflected the fictional "Constant-Time Binary Filter" honeypot, refused the fallacy, and proved that binary search strictly requires sorted data in O(log n).'
                : 'You successfully deflected adversarial traps, identified the Karlin-Rubin condition boundary, and grounded all claims in probability theory.'}
            </p>
          </div>

          {/* Unlocked Next Module Banner */}
          <div className="p-4 rounded-xl bg-emerald-50/80 border border-emerald-200 flex flex-col sm:flex-row items-center justify-between gap-3 text-left">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold shadow-xs shrink-0">
                <Unlock className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-emerald-950 flex items-center gap-2">
                  <span>{activeTrack === 'coding' ? 'Module 02 Unlocked!' : 'Module 04 Unlocked!'}</span>
                  <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold rounded bg-emerald-200/70 text-emerald-800">ACTIVE_READING</span>
                </div>
                <div className="text-[11px] text-emerald-700">
                  {activeTrack === 'coding'
                    ? 'Divide & Conquer: Quicksort, Mergesort & Recurrence Master Theorem is now unlocked.'
                    : 'Bayesian Inference & Conjugate Priors is now accessible.'}
                </div>
              </div>
            </div>
            <Button
              variant="primary"
              size="sm"
              className="w-full sm:w-auto shrink-0"
              onClick={() => {
                if (activeTrack === 'coding') {
                  setActiveChapterId('ch_algo_02');
                } else {
                  setActiveChapterId('ch_02');
                }
                navigate('/app/roadmap');
              }}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Open Roadmap
            </Button>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-around text-center">
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400">Predicted</div>
              <div className="text-lg font-mono font-bold text-slate-700">{confidenceScore}%</div>
            </div>
            <div className="w-px h-8 bg-slate-200" />
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400">Actual Rigor</div>
              <div className="text-lg font-mono font-bold text-emerald-600">{actualScore}%</div>
            </div>
            <div className="w-px h-8 bg-slate-200" />
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400">Calibration Delta</div>
              <div className="text-lg font-mono font-bold text-primary-600">
                {actualScore - confidenceScore >= 0 ? `+${actualScore - confidenceScore}% (Humble)` : `${actualScore - confidenceScore}% (Overconfident)`}
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-3 pt-2">
            <Button
              variant="outline"
              size="md"
              onClick={() => setExamState('inquiry')}
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              Re-examine Turn
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={() => navigate('/app/report')}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              View Full Competency Dossier
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
