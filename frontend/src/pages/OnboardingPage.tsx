import React, { useState } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Mic,
  BrainCircuit,
  ShieldCheck,
  ChevronRight,
  Check,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedRigor, setSelectedRigor] = useState('academic');
  const [micChecked, setMicChecked] = useState(false);
  const [oathAgreed, setOathAgreed] = useState(false);

  const handleNext = () => {
    if (step < 3) {
      setStep((step + 1) as any);
    } else {
      navigate('/app/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 font-sans antialiased">
      <div className="max-w-xl mx-auto w-full space-y-6">
        {/* Stepper Progress */}
        <div className="flex items-center justify-between px-2">
          {[
            { num: 1, label: 'Cognitive Rigor' },
            { num: 2, label: 'Vocal Audio' },
            { num: 3, label: 'Dialectic Oath' },
          ].map((item) => (
            <div key={item.num} className="flex items-center gap-2">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  step === item.num
                    ? 'bg-primary-600 text-white ring-4 ring-primary-100'
                    : step > item.num
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-200 text-slate-500'
                }`}
              >
                {step > item.num ? '✓' : item.num}
              </div>
              <span className="text-xs font-semibold text-slate-700 hidden sm:inline">
                {item.label}
              </span>
            </div>
          ))}
        </div>

        {/* Card Body */}
        <Card className="p-8 bg-white border border-slate-200 shadow-card space-y-6 animate-in fade-in duration-150">
          {/* Step 1 */}
          {step === 1 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <Badge variant="primary" size="sm">
                  Step 1 of 3
                </Badge>
                <h2 className="text-xl font-extrabold text-slate-900">
                  Select Your Inquiry Standard
                </h2>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Assay questions your answers. Choose how strictly the AI Examiner should challenge your premises.
                </p>
              </div>

              <div className="space-y-3">
                {[
                  {
                    id: 'foundational',
                    title: 'Bloom L3: Foundational',
                    desc: 'Focus on clear definitions, mental models, and standard textbook scenarios.',
                  },
                  {
                    id: 'applied',
                    title: 'Bloom L4: Applied Systems',
                    desc: 'Test failure modes, edge cases, and practical trade-off balances.',
                  },
                  {
                    id: 'academic',
                    title: 'Bloom L5: First-Principles (Recommended)',
                    desc: 'Adversarial counter-arguments, causal invariance proofs, and formal dialectic defense.',
                  },
                ].map((tier) => (
                  <div
                    key={tier.id}
                    onClick={() => setSelectedRigor(tier.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedRigor === tier.id
                        ? 'border-primary-600 bg-primary-50/60 ring-2 ring-primary-500/20'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900">
                        {tier.title}
                      </span>
                      {selectedRigor === tier.id && (
                        <Check className="w-4 h-4 text-primary-600" />
                      )}
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      {tier.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 2 */}
          {step === 2 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <Badge variant="purple" size="sm">
                  Step 2 of 3
                </Badge>
                <h2 className="text-xl font-extrabold text-slate-900">
                  Calibrate Microphone for Oral Defense
                </h2>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Oral defense exams use live vocal inquiry. Test your microphone input clarity.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900 text-white text-center space-y-4">
                <button
                  onClick={() => setMicChecked(true)}
                  className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto transition-transform ${
                    micChecked
                      ? 'bg-emerald-500 text-white ring-4 ring-emerald-500/30'
                      : 'bg-primary-600 text-white hover:scale-105'
                  }`}
                >
                  <Mic className="w-7 h-7" />
                </button>

                <div>
                  <div className="text-xs font-bold">
                    {micChecked ? 'Audio Input Calibrated!' : 'Click to test microphone'}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    {micChecked
                      ? 'High fidelity 48kHz audio stream verified'
                      : 'Speak a few words to calibrate noise floor'}
                  </div>
                </div>

                {/* Animated sound bars */}
                <div className="flex items-center justify-center gap-1.5 h-8">
                  {[20, 45, 75, 90, 60, 40, 80, 50, 30].map((h, i) => (
                    <div
                      key={i}
                      className={`w-1.5 rounded-full transition-all ${
                        micChecked ? 'bg-emerald-400' : 'bg-slate-700'
                      }`}
                      style={{ height: micChecked ? `${h}%` : '20%' }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3 */}
          {step === 3 && (
            <div className="space-y-5">
              <div className="space-y-1">
                <Badge variant="success" size="sm">
                  Step 3 of 3
                </Badge>
                <h2 className="text-xl font-extrabold text-slate-900">
                  The Socratic Learner Oath
                </h2>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Assay is designed to replace superficial recall with unyielding critical thinking.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-3 leading-relaxed">
                <div className="flex items-start gap-2.5">
                  <ShieldCheck className="w-5 h-5 text-primary-600 shrink-0 mt-0.5" />
                  <p>
                    I understand that the AI Examiner will deliberately introduce <strong>adversarial fallacy traps</strong> to test my vigilance, and I will point them out rather than blindly accepting them.
                  </p>
                </div>
                <div className="flex items-start gap-2.5">
                  <ShieldCheck className="w-5 h-5 text-primary-600 shrink-0 mt-0.5" />
                  <p>
                    I will formulate original arguments from <strong>first principles</strong> rather than seeking quick answer generation.
                  </p>
                </div>
              </div>

              <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-slate-900 pt-1">
                <input
                  type="checkbox"
                  checked={oathAgreed}
                  onChange={(e) => setOathAgreed(e.target.checked)}
                  className="w-4 h-4 rounded text-primary-600 border-slate-300 focus:ring-primary-500"
                />
                <span>I commit to active dialectic defense</span>
              </label>
            </div>
          )}

          {/* Footer Controls */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            {step > 1 ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setStep((step - 1) as any)}
              >
                Back
              </Button>
            ) : (
              <div />
            )}

            <Button
              variant="primary"
              size="md"
              disabled={step === 3 && !oathAgreed}
              onClick={handleNext}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              {step === 3 ? 'Complete & Enter Workspace' : 'Continue'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};
