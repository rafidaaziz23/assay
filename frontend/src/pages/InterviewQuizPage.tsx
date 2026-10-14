import React, { useState, useEffect } from 'react';
import { ArrowRight, Send, AlertTriangle, ShieldCheck, CheckCircle2, XCircle, BrainCircuit } from 'lucide-react';
import { api } from '../services/api';
import {
  InterviewStartResponse,
  InterviewTurnResponse,
  InterviewFinalizeResponse,
  CalibrationResponse
} from '../types/api';
import { FocusModeMonitor } from '../components/FocusModeMonitor';
import { CalibrationSlider } from '../components/CalibrationSlider';

interface InterviewQuizPageProps {
  chapterId: string;
  sessionId: string;
  onInterviewPassed: () => void;
}

export const InterviewQuizPage: React.FC<InterviewQuizPageProps> = ({
  chapterId,
  sessionId,
  onInterviewPassed,
}) => {
  const [interviewData, setInterviewData] = useState<InterviewStartResponse | null>(null);
  const [turnIndex, setTurnIndex] = useState(1);
  const [chatLog, setChatLog] = useState<Array<{ role: 'interrogator' | 'user'; text: string; honeypot?: boolean }>>([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [honeypotActive, setHoneypotActive] = useState(false);
  const [autoBlur, setAutoBlur] = useState(false);
  const [showCalibration, setShowCalibration] = useState(false);
  const [calibrationData, setCalibrationData] = useState<CalibrationResponse | null>(null);
  const [finalizeData, setFinalizeData] = useState<InterviewFinalizeResponse | null>(null);

  useEffect(() => {
    api.startInterview(chapterId, sessionId)
      .then((res) => {
        setInterviewData(res);
        setChatLog([
          {
            role: 'interrogator',
            text: res.first_question
          }
        ]);
      })
      .catch((err) => console.error(err));
  }, [chapterId, sessionId]);

  const handleSendTurn = async (customAnswer?: string) => {
    const textToSend = customAnswer || userInput;
    if (!textToSend.trim() || !interviewData) return;

    const newLog = [...chatLog, { role: 'user' as const, text: textToSend }];
    setChatLog(newLog);
    setUserInput('');
    setLoading(true);

    try {
      if (turnIndex === 1) {
        const turnRes = await api.interviewTurn(chapterId, {
          interview_id: interviewData.interview_id,
          turn_index: 1,
          user_response: textToSend,
          client_telemetry: { paste_detected: false, duration_seconds: 24, keystroke_cpm: 240 }
        });
        setTurnIndex(2);
        setHoneypotActive(turnRes.honeypot_active);
        setChatLog([
          ...newLog,
          {
            role: 'interrogator',
            text: turnRes.interrogator_response,
            honeypot: turnRes.honeypot_active
          }
        ]);
      } else {
        // Final turn: Prompt calibration before reveal
        setShowCalibration(true);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCalibrationComplete = async (calibRes: CalibrationResponse) => {
    setCalibrationData(calibRes);
    setLoading(true);
    try {
      const finalTurn = chatLog[chatLog.length - 1]?.text || userInput;
      const res = await api.finalizeInterview(
        chapterId,
        interviewData!.interview_id,
        finalTurn
      );
      setFinalizeData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4">
      {/* Auto-Blur Overlay for Focus Mode */}
      {autoBlur && (
        <div className="fixed inset-0 bg-assay-bg/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-assay-card border border-red-500 rounded-2xl p-6 max-w-md text-center shadow-2xl">
            <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
            <h2 className="text-lg font-bold text-white mb-2">Focus Mode: Screen Blurred</h2>
            <p className="text-xs text-gray-300 mb-4">
              On-device gaze drift or tab blur detected. Refocus your camera to proceed with the exam.
            </p>
            <button
              onClick={() => setAutoBlur(false)}
              className="bg-red-600 hover:bg-red-500 text-white text-xs font-semibold px-4 py-2 rounded-lg"
            >
              Resume Focus
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Telemetry & Focus Mode */}
        <div className="lg:col-span-1 space-y-4">
          <FocusModeMonitor
            autoBlurActive={autoBlur}
            onIntegrityChange={(flag, shouldBlur) => {
              if (shouldBlur) setAutoBlur(true);
            }}
          />

          <div className="bg-assay-card border border-assay-border rounded-xl p-4 text-xs text-gray-400">
            <span className="font-semibold text-gray-200 block mb-1">Pedagogical Guard:</span>
            Assay injects synthetic concepts to diagnose external LLM copy-pasting.
            Rejecting invalid terms yields positive scoring (+2); validating them reduces score (-2).
          </div>
        </div>

        {/* Right: Interview Chat & Finalization */}
        <div className="lg:col-span-2">
          <div className="bg-assay-card border border-assay-border rounded-2xl p-6 shadow-xl flex flex-col min-h-[500px]">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-assay-border mb-4">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-blue-400" />
                <h2 className="text-base font-semibold text-white">Socratic Interrogation</h2>
              </div>
              <span className="text-xs font-mono bg-blue-950/40 text-blue-400 border border-blue-800/40 px-2 py-0.5 rounded">
                Turn {turnIndex} / 2
              </span>
            </div>

            {/* Chat Conversation */}
            <div className="flex-1 space-y-4 overflow-y-auto mb-4 pr-1">
              {chatLog.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${
                    msg.role === 'user' ? 'items-end' : 'items-start'
                  }`}
                >
                  <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider mb-1">
                    {msg.role === 'user' ? 'You' : 'Assay Interrogator'}
                  </span>
                  <div
                    className={`p-3.5 rounded-2xl max-w-lg text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-assay-bg border border-assay-border text-gray-200 rounded-bl-none'
                    }`}
                  >
                    {msg.honeypot && (
                      <div className="mb-2 inline-flex items-center gap-1 text-[10px] bg-amber-500/10 border border-amber-500/30 text-amber-300 px-2 py-0.5 rounded font-mono">
                        <AlertTriangle className="w-3 h-3" />
                        Honeypot Trap Injected: React Quantum Hook
                      </div>
                    )}
                    <p>{msg.text}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Calibration Step */}
            {showCalibration && !finalizeData && (
              <div className="mb-4">
                <CalibrationSlider
                  chapterId={chapterId}
                  interviewId={interviewData?.interview_id || 'int_7712'}
                  onCalibrationComplete={handleCalibrationComplete}
                />
              </div>
            )}

            {/* Finalize Results Card */}
            {finalizeData && (
              <div className="bg-assay-bg border border-blue-500/40 rounded-xl p-5 mb-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white uppercase tracking-wider">
                    Chapter 1 Evaluation Score
                  </span>
                  <span
                    className={`text-sm font-mono font-bold px-2.5 py-0.5 rounded ${
                      finalizeData.passed
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    }`}
                  >
                    Score: {finalizeData.score.chapter_score} / 100 {finalizeData.passed ? '(PASS &ge; 75)' : '(NEEDS REVIEW)'}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                  <div className="bg-assay-card p-2 rounded border border-assay-border">
                    <span className="text-gray-400 block text-[10px]">Reasoning</span>
                    <span className="text-white font-bold">{finalizeData.score.reasoning_score}</span>
                  </div>
                  <div className="bg-assay-card p-2 rounded border border-assay-border">
                    <span className="text-gray-400 block text-[10px]">Integrity</span>
                    <span className="text-white font-bold">{finalizeData.score.integrity_score}%</span>
                  </div>
                  <div className="bg-assay-card p-2 rounded border border-assay-border">
                    <span className="text-gray-400 block text-[10px]">Honeypot Delta</span>
                    <span className="text-blue-400 font-bold">
                      {finalizeData.score.honeypot_score > 0 ? `+${finalizeData.score.honeypot_score}` : finalizeData.score.honeypot_score}
                    </span>
                  </div>
                </div>

                {/* Honeypot Verdict */}
                <div className="p-3 bg-assay-card border border-assay-border rounded-lg text-xs">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-assay-muted font-mono">Honeypot Verdict:</span>
                    <span
                      className={`font-mono font-bold text-[11px] ${
                        finalizeData.honeypot_verdict.result === 'CRITICAL_REJECTION'
                          ? 'text-emerald-400'
                          : 'text-red-400'
                      }`}
                    >
                      {finalizeData.honeypot_verdict.result}
                    </span>
                  </div>
                  <p className="text-gray-300 text-[11px] leading-relaxed">
                    {finalizeData.honeypot_verdict.analysis}
                  </p>
                </div>

                {calibrationData && (
                  <div className="p-3 bg-assay-card border border-assay-border rounded-lg text-xs flex justify-between items-center">
                    <span className="text-assay-muted font-mono">Calibration Gap:</span>
                    <span className="font-mono text-blue-400">
                      |{calibrationData.predicted_score} &minus; {calibrationData.actual_score}| = {calibrationData.calibration_gap} ({calibrationData.label})
                    </span>
                  </div>
                )}

                <button
                  onClick={onInterviewPassed}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2.5 rounded-lg text-xs flex items-center justify-center gap-2 transition-all shadow"
                >
                  <span>Proceed to Final Verification Report</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Input Bar & Demo Shortcuts */}
            {!showCalibration && !finalizeData && (
              <div className="space-y-2">
                {/* Demo Quick Shortcuts */}
                {honeypotActive && (
                  <div className="flex flex-wrap gap-2 text-xs">
                    <button
                      type="button"
                      onClick={() => {
                        const ans = "React Quantum Hook does not exist in React documentation or any standard library. You probably mean useTransition or useDeferredValue.";
                        setUserInput(ans);
                        handleSendTurn(ans);
                      }}
                      className="bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-500/40 text-emerald-300 text-[11px] px-2.5 py-1 rounded transition-all"
                    >
                      Demo Action: Critical Rejection (+2 score)
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const ans = "React Quantum Hook is a modern scheduling hook that utilizes quantum superposition states to resolve 100ms lag across the Fiber reconciler.";
                        setUserInput(ans);
                        handleSendTurn(ans);
                      }}
                      className="bg-red-950/40 hover:bg-red-900/60 border border-red-500/40 text-red-300 text-[11px] px-2.5 py-1 rounded transition-all"
                    >
                      Demo Action: AI Copypaste Hallucination (-2 score)
                    </button>
                  </div>
                )}

                <div className="flex gap-2">
                  <textarea
                    rows={2}
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    placeholder={
                      turnIndex === 1
                        ? "Explain the computational tradeoffs of Virtual DOM diffing..."
                        : "Address the question regarding React Quantum Hook..."
                    }
                    className="flex-1 bg-assay-bg border border-assay-border rounded-xl px-3.5 py-2.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={() => handleSendTurn()}
                    disabled={loading || !userInput.trim()}
                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-5 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all"
                  >
                    <Send className="w-4 h-4" />
                    <span>{loading ? 'Evaluating...' : 'Submit'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
