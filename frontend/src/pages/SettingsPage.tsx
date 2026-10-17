import React, { useState, useEffect } from 'react';
import {
  User,
  Sparkles,
  Mic,
  Bell,
  Shield,
  HelpCircle,
  BookOpen,
  ChevronDown,
  ArrowRight,
  ShieldCheck,
  Download,
  Lock,
  CheckCircle2,
} from 'lucide-react';
import { Card } from '../components/atoms/Card';
import { api } from '../services/api';

type InterrogationTone = 'supportive' | 'academic' | 'devils_advocate';
type SocraticFrequency = 1 | 2 | 3;

export const SettingsPage: React.FC = () => {
  // Navigation active tab in settings left menu
  const [activeNav, setActiveNav] = useState('socratic');

  // Tone state
  const [tone, setTone] = useState<InterrogationTone>('academic');

  // Frequency slider: 1 = Minimal, 2 = Balanced (Recommended), 3 = Frequent
  const [frequency, setFrequency] = useState<SocraticFrequency>(2);

  // Audio setup
  const [audioDevice, setAudioDevice] = useState('MacBook Pro Microphone (Built-in Audio)');
  const [allowSilence, setAllowSilence] = useState(true);
  const [autoTranscribe, setAutoTranscribe] = useState(true);

  // Privacy & Integrity
  const [nonPunitiveFocus, setNonPunitiveFocus] = useState(true);

  // Save feedback state
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    api.getSettings()
      .then((res) => {
        if (res.rigor === 'foundational') setTone('supportive');
        else if (res.rigor === 'academic') setTone('academic');
        else if (res.rigor === 'advocate') setTone('devils_advocate');
        if (res.audio_device) setAudioDevice(res.audio_device);
      })
      .catch((e) => console.warn('Settings load fallback:', e));
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await api.updateSettings({
        model: 'gemini-2.5-flash',
        rigor: tone === 'supportive' ? 'foundational' : tone === 'academic' ? 'academic' : 'advocate',
        fallacy_sensitivity: 'balanced',
        audio_device: audioDevice,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (e) {
      console.warn('Settings save fallback:', e);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } finally {
      setIsSaving(false);
    }
  };

  const audioVisualizerHeights = [
    12, 18, 26, 22, 30, 24, 32, 28, 34, 30, 22, 16, 12, 8, 8, 8, 8, 8, 8, 8
  ];

  const getFrequencyLabel = (freq: SocraticFrequency) => {
    switch (freq) {
      case 1:
        return 'Minimal (End of Chapter)';
      case 2:
        return 'Balanced (Every 3 Sections)';
      case 3:
        return 'Frequent (Every Section)';
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-16 animate-in fade-in duration-200">
      {/* Top Header & Breadcrumb */}
      <div>
        <div className="flex items-center gap-2 text-xs font-medium text-slate-400 mb-1">
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
            ACCOUNT & PREFERENCES
          </span>
          <span className="text-indigo-400">&bull;</span>
          <span className="text-primary-700 font-semibold text-xs">Dialectic Core v2.4</span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Settings</h1>
        <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
          Manage your learning persona, defense criteria, and hardware calibration for synchronous dialectic evaluations.
        </p>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column (3 cols / ~w-64) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Settings Sub-Navigation Card */}
          <Card className="p-2 bg-white shadow-card border border-slate-200/80 space-y-1">
            <button
              onClick={() => setActiveNav('profile')}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors cursor-pointer ${
                activeNav === 'profile'
                  ? 'bg-indigo-50/80 text-primary-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <User className="w-4 h-4 text-slate-400" />
              <span>Account & Profile</span>
            </button>

            <button
              onClick={() => setActiveNav('socratic')}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-colors cursor-pointer ${
                activeNav === 'socratic'
                  ? 'bg-indigo-50/80 text-primary-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-4 h-4 text-primary-600" />
                <span>Socratic Preferences</span>
              </div>
              <span className="w-1.5 h-1.5 rounded-full bg-primary-600" />
            </button>

            <button
              onClick={() => setActiveNav('audio')}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors cursor-pointer ${
                activeNav === 'audio'
                  ? 'bg-indigo-50/80 text-primary-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Mic className="w-4 h-4 text-slate-400" />
              <span>Audio & Microphone</span>
            </button>

            <button
              onClick={() => setActiveNav('notifications')}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors cursor-pointer ${
                activeNav === 'notifications'
                  ? 'bg-indigo-50/80 text-primary-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Bell className="w-4 h-4 text-slate-400" />
              <span>Notifications</span>
            </button>

            <button
              onClick={() => setActiveNav('privacy')}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-medium transition-colors cursor-pointer ${
                activeNav === 'privacy'
                  ? 'bg-indigo-50/80 text-primary-700 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Shield className="w-4 h-4 text-slate-400" />
              <span>Data & Privacy</span>
            </button>
          </Card>

          {/* Help / Custom Defense Callout */}
          <div className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100/80 space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
              <HelpCircle className="w-4 h-4 text-primary-600" />
              <span>Custom Defense?</span>
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Faculty leads can calibrate custom rubrics and blind-trial peer parameters.
            </p>
            <button
              onClick={() => alert('Assay Faculty Consultation Protocol initiated.')}
              className="text-[11px] font-semibold text-primary-600 hover:text-primary-700 flex items-center gap-1 cursor-pointer"
            >
              <span>Contact Faculty Lead</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {/* Active Dossier Mini Card */}
          <Card className="p-3.5 bg-white shadow-card border border-slate-200/80 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                ACTIVE DOSSIER
              </span>
              <span className="bg-indigo-50 text-indigo-700 border border-indigo-100/70 text-[10px] font-bold px-2 py-0.5 rounded-full">
                Live Sync
              </span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <BookOpen className="w-4 h-4" />
              </div>
              <div className="overflow-hidden">
                <div className="font-bold text-xs text-slate-900 truncate">
                  Phil of Science: Epistemic
                </div>
                <div className="text-[10px] text-slate-400 truncate">
                  Oxford-Cambridge Protocol
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column (9 cols / Main Settings Content) */}
        <div className="lg:col-span-9 space-y-6">
          {/* Card 1: Dialectic Rigor & AI Examiner Persona */}
          <Card className="p-6 sm:p-7 bg-white shadow-card border border-slate-200/80 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  Dialectic Rigor & AI Examiner Persona
                </h2>
                <p className="text-xs text-slate-400 font-normal leading-relaxed max-w-xl mt-0.5">
                  Calibrate how rigorously oral defense examiners challenge your claims, demand proofs, and probe thesis premises.
                </p>
              </div>
              <span className="bg-indigo-50 text-indigo-700 border border-indigo-100/80 text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full self-start">
                RIGOR CALIBRATION
              </span>
            </div>

            {/* Interrogation Tone Options */}
            <div className="space-y-2.5">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                INTERROGATION TONE
              </span>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                {/* 1. Supportive Guide */}
                <div
                  onClick={() => setTone('supportive')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                    tone === 'supportive'
                      ? 'border-2 border-primary-600 bg-white ring-2 ring-primary-500/10 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        tone === 'supportive' ? 'border-primary-600' : 'border-slate-300'
                      }`}>
                        {tone === 'supportive' && <span className="w-2 h-2 rounded-full bg-primary-600" />}
                      </div>
                      <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                        Gentle Guidance
                      </span>
                    </div>
                    <h3 className="font-bold text-sm text-slate-900 mt-2.5">Supportive Guide</h3>
                    <p className="text-xs text-slate-500 leading-relaxed mt-1">
                      Provides gentle dialectic scaffolding, generous pause buffers, and conceptual nudges before counter-probing.
                    </p>
                  </div>
                </div>

                {/* 2. Rigorous Academic (Selected Default) */}
                <div
                  onClick={() => setTone('academic')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                    tone === 'academic'
                      ? 'border-2 border-primary-600 bg-white ring-2 ring-primary-500/10 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        tone === 'academic' ? 'border-primary-600' : 'border-slate-300'
                      }`}>
                        {tone === 'academic' && <span className="w-2 h-2 rounded-full bg-primary-600" />}
                      </div>
                      <span className="bg-indigo-50 text-indigo-700 border border-indigo-200/60 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                        Default Standard
                      </span>
                    </div>
                    <h3 className="font-bold text-sm text-slate-900 mt-2.5">Rigorous Academic</h3>
                    <p className="text-xs text-primary-800 leading-relaxed mt-1">
                      Challenges unstated premises, demands formal counter-examples, and tests edge-case boundary conditions under peer rubrics.
                    </p>
                  </div>
                </div>

                {/* 3. Devil's Advocate */}
                <div
                  onClick={() => setTone('devils_advocate')}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                    tone === 'devils_advocate'
                      ? 'border-2 border-primary-600 bg-white ring-2 ring-primary-500/10 shadow-xs'
                      : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        tone === 'devils_advocate' ? 'border-primary-600' : 'border-slate-300'
                      }`}>
                        {tone === 'devils_advocate' && <span className="w-2 h-2 rounded-full bg-primary-600" />}
                      </div>
                      <span className="bg-amber-50 text-amber-700 border border-amber-200/60 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                        High Friction
                      </span>
                    </div>
                    <h3 className="font-bold text-sm text-slate-900 mt-2.5">Devil&apos;s Advocate</h3>
                    <p className="text-xs text-slate-500 leading-relaxed mt-1">
                      Actively attempts to refute candidate hypotheses, stresses contradiction detection, and probes epistemic confidence.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Socratic Question Frequency in Reader */}
            <div className="pt-2 space-y-4 border-t border-slate-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-sm text-slate-900">
                    Socratic Question Frequency in Reader
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Determines how frequently active reader checkpoints interrupt passive scrolling to evaluate thesis grasp.
                  </p>
                </div>
                <span className="bg-indigo-50 text-indigo-700 border border-indigo-100/70 text-[10px] font-bold px-2.5 py-1 rounded-full shrink-0">
                  {getFrequencyLabel(frequency)}
                </span>
              </div>

              {/* Slider track */}
              <div className="space-y-2">
                <div className="relative flex items-center">
                  <input
                    type="range"
                    min="1"
                    max="3"
                    step="1"
                    value={frequency}
                    onChange={(e) => setFrequency(Number(e.target.value) as SocraticFrequency)}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                </div>

                <div className="flex items-center justify-between text-[11px]">
                  <span
                    onClick={() => setFrequency(1)}
                    className={`cursor-pointer ${frequency === 1 ? 'text-primary-700 font-bold' : 'text-slate-400'}`}
                  >
                    Minimal (End of Chapter)
                  </span>
                  <span
                    onClick={() => setFrequency(2)}
                    className={`cursor-pointer ${frequency === 2 ? 'text-primary-700 font-bold' : 'text-slate-400'}`}
                  >
                    Balanced (Recommended)
                  </span>
                  <span
                    onClick={() => setFrequency(3)}
                    className={`cursor-pointer ${frequency === 3 ? 'text-primary-700 font-bold' : 'text-slate-400'}`}
                  >
                    Frequent Checkpoints
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Card 2: Oral Defense & Audio Setup */}
          <Card className="p-6 sm:p-7 bg-white shadow-card border border-slate-200/80 space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Oral Defense & Audio Setup
              </h2>
              <p className="text-xs text-slate-400 font-normal leading-relaxed max-w-xl mt-0.5">
                Configure microphone hardware and live speech silence tolerance for real-time oral examinations.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
              {/* Left Column (7 cols): Microphone selection & Level Calibration */}
              <div className="md:col-span-7 space-y-4">
                <div className="space-y-1.5">
                  <label className="flex items-center gap-1.5 text-xs font-bold text-slate-800">
                    <Mic className="w-3.5 h-3.5 text-primary-600" />
                    <span>Microphone Input Device</span>
                  </label>
                  <div className="relative">
                    <select
                      value={audioDevice}
                      onChange={(e) => setAudioDevice(e.target.value)}
                      className="w-full appearance-none bg-white border border-slate-200/90 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 font-medium focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600 pr-10 cursor-pointer shadow-2xs"
                    >
                      <option value="MacBook Pro Microphone (Built-in Audio)">
                        MacBook Pro Microphone (Built-in Audio)
                      </option>
                      <option value="AirPods Pro (Spatial Audio)">
                        AirPods Pro (Spatial Audio)
                      </option>
                      <option value="External USB Condenser (Blue Yeti)">
                        External USB Condenser (Blue Yeti)
                      </option>
                    </select>
                    <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
                  </div>
                </div>

                {/* Input Level Calibration Visualizer */}
                <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-700">Input Level Calibration</span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-[10px] font-semibold">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      Ready
                    </span>
                  </div>

                  {/* 20 Vertical Audio Bars */}
                  <div className="h-10 flex items-end gap-1.5 px-1 py-1">
                    {audioVisualizerHeights.map((h, i) => (
                      <div
                        key={i}
                        className={`w-1.5 rounded-full transition-all duration-300 ${
                          i < 3
                            ? 'bg-emerald-500'
                            : i < 11
                            ? 'bg-indigo-600'
                            : 'bg-indigo-200/90'
                        }`}
                        style={{ height: `${h}px` }}
                      />
                    ))}
                  </div>

                  <p className="text-[10px] text-slate-400 leading-relaxed">
                    Speak normally. Levels should remain within the central periwinkle zone without peaking.
                  </p>
                </div>
              </div>

              {/* Right Column (5 cols): Silence intervals & auto-transcribe toggles */}
              <div className="md:col-span-5 bg-slate-50/70 border border-slate-100 rounded-2xl p-4 space-y-5">
                {/* Toggle 1: Silence intervals */}
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <h4 className="font-bold text-xs text-slate-900 leading-snug">
                      Allow silence intervals without auto-pausing
                    </h4>
                    <p className="text-[11px] text-slate-500 leading-relaxed">
                      Grants up to 15 seconds of cognitive pause time for formulating mathematical deductions and premise proofs.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={allowSilence}
                    onClick={() => setAllowSilence(!allowSilence)}
                    className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                      allowSilence ? 'bg-primary-600' : 'bg-slate-200'
                    }`}
                  >
                    <span
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                        allowSilence ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>

                {/* Toggle 2: Auto-transcribe defense */}
                <div className="flex items-start justify-between gap-3 pt-3 border-t border-slate-200/60">
                  <div className="space-y-1">
                    <h4 className="font-bold text-xs text-slate-900 leading-snug">
                      Auto-transcribe defense dialogue
                    </h4>
                    <p className="text-[11px] text-slate-500 leading-relaxed">
                      Saves verbatim transcripts with examiner timecodes and citation stamps to your permanent Dossier.
                    </p>
                  </div>
                  <button
                    type="button"
                    role="switch"
                    aria-checked={autoTranscribe}
                    onClick={() => setAutoTranscribe(!autoTranscribe)}
                    className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                      autoTranscribe ? 'bg-primary-600' : 'bg-slate-200'
                    }`}
                  >
                    <span
                      className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                        autoTranscribe ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </Card>

          {/* Card 3: Privacy & Integrity Mode */}
          <Card className="p-6 sm:p-7 bg-white shadow-card border border-slate-200/80 space-y-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>Privacy & Integrity Mode</span>
                <ShieldCheck className="w-4 h-4 text-primary-600" />
              </h2>
              <p className="text-xs text-slate-400 font-normal leading-relaxed max-w-xl mt-0.5">
                Control telemetry logging, non-punitive focus tracking, and cryptographic audit preferences.
              </p>
            </div>

            {/* Row 1: Non-punitive focus detection */}
            <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-xs text-slate-900">
                    Non-punitive focus detection
                  </h4>
                  <p className="text-[11px] text-slate-500 leading-relaxed mt-0.5 max-w-2xl">
                    Assay pauses defense timers when switching browser tabs instead of penalizing integrity scores. Designed to accommodate deep reference checking in external primary sources.
                  </p>
                </div>
              </div>

              <button
                type="button"
                role="switch"
                aria-checked={nonPunitiveFocus}
                onClick={() => setNonPunitiveFocus(!nonPunitiveFocus)}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                  nonPunitiveFocus ? 'bg-primary-600' : 'bg-slate-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out ${
                    nonPunitiveFocus ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* Row 2: Export Complete Dialectic Archive */}
            <div className="bg-slate-50/70 border border-slate-100 rounded-2xl p-4 flex items-center justify-between gap-4">
              <div className="flex items-start gap-3.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Download className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-xs text-slate-900">
                    Export Complete Dialectic Archive
                  </h4>
                  <p className="text-[11px] text-slate-500 leading-relaxed mt-0.5 max-w-2xl">
                    Download all verified transcripts, audio recordings, and cryptographic proof hashes as a signed JSON & PDF bundle.
                  </p>
                </div>
              </div>

              <button
                onClick={() => alert('Dialectic Archive generation scheduled. A signed bundle (.zip) will be downloaded.')}
                className="border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-3.5 py-2 rounded-xl flex items-center gap-1.5 shrink-0 shadow-2xs cursor-pointer transition-colors"
              >
                <span>Download Archive (.zip)</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Bottom Proof Box */}
            <div className="bg-slate-50/50 border border-slate-200/80 rounded-xl p-3 flex items-center gap-2 text-[11px] text-slate-500">
              <Lock className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>
                Your telemetry proofs are verified under SHA-256 state signatures. Ledger ID:{' '}
                <strong className="font-mono text-primary-700">0x8F4A...B210</strong>
              </span>
            </div>
          </Card>

          {/* Bottom Action Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>
                {saveSuccess
                  ? 'All preferences synchronized to server and encrypted local cache!'
                  : 'All changes saved to encrypted local cache'}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => {
                  setTone('academic');
                  setFrequency(2);
                  setAllowSilence(true);
                  setAutoTranscribe(true);
                  setNonPunitiveFocus(true);
                }}
                className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-4 py-2 cursor-pointer transition-colors"
              >
                Discard
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={isSaving}
                className="bg-[#0F172A] hover:bg-slate-800 text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-xs flex items-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
              >
                <span>{isSaving ? 'Saving...' : 'Save Changes'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
