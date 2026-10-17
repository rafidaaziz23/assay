import React, { useState } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Input } from '../components/atoms/Input';
import {
  Settings,
  Brain,
  Mic,
  Sliders,
  Shield,
  Bell,
  Check,
  Save,
  Key,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [model, setModel] = useState('gemini-2.5-flash');
  const [rigor, setRigor] = useState('academic');
  const [fallacySensitivity, setFallacySensitivity] = useState('balanced');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-in fade-in duration-200 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Settings & Socratic Calibration
        </h1>
        <p className="text-xs text-slate-500">
          Configure model inference, audio hardware, and dialectic examiner parameters.
        </p>
      </div>

      {/* Model & Inference Engine */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
          <Brain className="w-5 h-5 text-primary-600" />
          <h2 className="text-sm font-bold text-slate-900">
            Socratic Reasoning Engine
          </h2>
        </div>

        <div className="space-y-3">
          <label className="text-xs font-semibold text-slate-700">
            Active LLM Orchestrator
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              {
                id: 'gemini-2.5-flash',
                name: 'Gemini 2.5 Flash',
                tag: 'Recommended (Fast)',
              },
              {
                id: 'claude-3-5-sonnet',
                name: 'Claude 3.5 Sonnet',
                tag: 'Deep Synthesis',
              },
              {
                id: 'gpt-4o',
                name: 'GPT-4o',
                tag: 'High Reliability',
              },
            ].map((m) => (
              <div
                key={m.id}
                onClick={() => setModel(m.id)}
                className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all ${
                  model === m.id
                    ? 'border-primary-600 bg-primary-50/50 ring-2 ring-primary-500/20'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="font-bold text-slate-900">{m.name}</div>
                <div className="text-[10px] text-primary-700 font-medium mt-0.5">
                  {m.tag}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Socratic Rigor Calibration */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
          <Sliders className="w-5 h-5 text-primary-600" />
          <h2 className="text-sm font-bold text-slate-900">
            Dialectic Examiner Rigor
          </h2>
        </div>

        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between text-xs font-semibold mb-1">
              <span className="text-slate-800">Target Cognitive Tier</span>
              <span className="font-mono text-primary-600 font-bold uppercase">
                {rigor}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[
                { id: 'foundational', label: 'Bloom L3 (Concept)' },
                { id: 'applied', label: 'Bloom L4 (Mechanisms)' },
                { id: 'academic', label: 'Bloom L5 (Synthesis)' },
              ].map((r) => (
                <button
                  key={r.id}
                  onClick={() => setRigor(r.id)}
                  className={`py-2 px-3 rounded-lg text-xs font-medium border transition-all ${
                    rigor === r.id
                      ? 'bg-slate-900 text-white border-slate-900'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs font-semibold mb-1">
              <span className="text-slate-800">Adversarial Honeypot Sensitivity</span>
              <Badge variant="warning" size="sm">
                Active Traps
              </Badge>
            </div>
            <p className="text-[11px] text-slate-500 mb-2">
              Frequency of intentional subtle fallacies introduced by the examiner to test your critical vigilance.
            </p>
            <div className="grid grid-cols-3 gap-2">
              {['lenient', 'balanced', 'aggressive'].map((s) => (
                <button
                  key={s}
                  onClick={() => setFallacySensitivity(s)}
                  className={`capitalize py-2 px-3 rounded-lg text-xs font-medium border transition-all ${
                    fallacySensitivity === s
                      ? 'bg-primary-600 text-white border-primary-600'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Audio Hardware Calibration */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
          <Mic className="w-5 h-5 text-purple-600" />
          <h2 className="text-sm font-bold text-slate-900">
            Audio & Speech-To-Text Hardware
          </h2>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-slate-700">
              Default Input Microphone
            </label>
            <select className="mt-1 w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500">
              <option>Default Microphone (High Definition Audio Device)</option>
              <option>USB Studio Condenser Mic (24-bit, 48kHz)</option>
              <option>Built-in System Array</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end pt-2">
        <Button
          variant="primary"
          size="md"
          onClick={handleSave}
          leftIcon={saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
        >
          {saved ? 'Settings Saved!' : 'Save Preferences'}
        </Button>
      </div>
    </div>
  );
};
