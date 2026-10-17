import React, { useState, useRef } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import {
  Search,
  FileText,
  RotateCcw,
  Layers,
  Cpu,
  Shield,
  GripVertical,
  Clock,
  ArrowRight,
  Check,
  X,
  FileUp,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';

export const IntakePage: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveSessionId, setActiveChapterId } = useAppStore();
  const [activeTab, setActiveTab] = useState<'prompt' | 'upload'>('prompt');
  const [topicPrompt, setTopicPrompt] = useState('How mRNA vaccines work');
  const [selectedDepth, setSelectedDepth] = useState<'foundation' | 'applied' | 'rigorous'>('applied');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedFileObj, setSelectedFileObj] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [uploadedFile, setUploadedFile] = useState<{
    name: string;
    size: string;
    pages: string;
  } | null>({
    name: 'MIT_6.042J_Discrete_Math_Syllabus.pdf',
    size: '4.2 MB',
    pages: '28 Pages',
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFileObj(file);
      setUploadedFile({
        name: file.name,
        size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        pages: '28 Pages',
      });
    }
  };

  const ALGO_MODULES = [
    { id: 'mod-1', title: '1. Algorithmic Complexity & Big-O Notation', concepts: '4 concepts', time: '45 min', badge: 'Recommended' as const, selected: true },
    { id: 'mod-2', title: '2. Divide and Conquer: QuickSort & MergeSort', concepts: '5 concepts', time: '1 hr 15 min', badge: null, selected: true },
    { id: 'mod-3', title: '3. Binary Search & Logarithmic Bounds', concepts: '4 concepts', time: '40 min', badge: null, selected: true },
    { id: 'mod-4', title: '4. Hash Tables & Collision Resolution', concepts: '5 concepts', time: '50 min', badge: null, selected: true },
    { id: 'mod-5', title: '5. Graph Traversals: BFS, DFS & Shortest Paths', concepts: '6 concepts', time: '1 hr 20 min', badge: null, selected: true },
    { id: 'mod-6', title: '6. Dynamic Programming & Optimal Substructure', concepts: '5 concepts', time: '1 hr 30 min', badge: 'Optional' as const, selected: false },
  ];

  const MATH_MODULES = [
    { id: 'mod-1', title: '1. Statistics for Decisions: Neyman–Pearson Lemma', concepts: '4 concepts', time: '45 min', badge: 'Recommended' as const, selected: true },
    { id: 'mod-2', title: '2. Causal Inference & Potential Outcomes', concepts: '5 concepts', time: '1 hr 15 min', badge: null, selected: true },
    { id: 'mod-3', title: '3. Maximum Likelihood & Score Equations', concepts: '4 concepts', time: '50 min', badge: null, selected: true },
    { id: 'mod-4', title: '4. Confidence Intervals & Duality with Testing', concepts: '4 concepts', time: '40 min', badge: null, selected: true },
    { id: 'mod-5', title: '5. Bayesian Inference & Loss Functions', concepts: '5 concepts', time: '1 hr', badge: 'Optional' as const, selected: false },
  ];

  const BIO_MODULES = [
    { id: 'mod-1', title: '1. Modified Nucleosides & Immune Evasion', concepts: '4 concepts', time: '45 min', badge: 'Recommended' as const, selected: true },
    { id: 'mod-2', title: '2. Lipid Nanoparticle (LNP) Formulation & Delivery', concepts: '5 concepts', time: '1 hr 15 min', badge: null, selected: true },
    { id: 'mod-3', title: '3. Ribosomal Translation & Antigen Presentation', concepts: '6 concepts', time: '1 hr 30 min', badge: null, selected: true },
    { id: 'mod-4', title: '4. Adjuvant Dynamics & T-Cell Activation', concepts: '3 concepts', time: '50 min', badge: null, selected: true },
    { id: 'mod-5', title: '5. Manufacturing Scale & Thermal Stability', concepts: '2 concepts', time: '40 min', badge: 'Optional' as const, selected: false },
  ];

  const [modules, setModules] = useState(ALGO_MODULES);

  React.useEffect(() => {
    const t = topicPrompt.toLowerCase();
    if (t.includes('algo') || t.includes('cod') || t.includes('sort') || t.includes('tree') || t.includes('graph') || t.includes('data struct')) {
      setModules(ALGO_MODULES);
    } else if (t.includes('math') || t.includes('stat') || t.includes('neyman') || t.includes('bayes') || t.includes('prob') || t.includes('decision')) {
      setModules(MATH_MODULES);
    } else if (t.includes('mrna') || t.includes('vaccine') || t.includes('bio') || t.includes('cell')) {
      setModules(BIO_MODULES);
    }
  }, [topicPrompt]);

  const toggleModule = (id: string) => {
    setModules((prev) =>
      prev.map((m) => (m.id === id ? { ...m, selected: !m.selected } : m))
    );
  };

  const selectedCount = modules.filter((m) => m.selected).length;

  const handleCommit = async () => {
    setIsSubmitting(true);
    try {
      const intakeRes = await api.createIntake({
        intent: topicPrompt,
        role: selectedDepth === 'rigorous' ? 'System Design' : (selectedDepth === 'applied' ? 'Data/ML' : 'Software Engineering'),
        document: selectedFileObj ? selectedFileObj.name : uploadedFile?.name,
      });

      const sid = intakeRes.session_id;
      setActiveSessionId(sid);

      if (selectedFileObj) {
        await api.uploadDocument(sid, selectedFileObj);
      }

      // Generate verified syllabus through backend engine
      const syl = await api.generateSyllabus(sid);
      if (syl && syl.chapters && syl.chapters.length > 0) {
        setActiveChapterId(syl.chapters[0].chapter_id);
      }
      navigate('/app/roadmap');
    } catch (err) {
      console.warn('Intake live generation failed, routing to active curriculum:', err);
      // If offline/error, choose closest track
      const t = topicPrompt.toLowerCase();
      if (t.includes('algo') || t.includes('cod') || t.includes('sort') || t.includes('data struct')) {
        setActiveSessionId('sess_coding_basic');
      } else if (t.includes('math') || t.includes('stat') || t.includes('neyman') || t.includes('decision')) {
        setActiveSessionId('sess_math_stats');
      }
      navigate('/app/roadmap');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12 animate-in fade-in duration-200">
      {/* Header Banner - Clean text without AI icons */}
      <div className="space-y-1.5">
        <div className="text-xs font-bold tracking-wider text-indigo-600 uppercase">
          NEW SUBJECT
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
          What do you want to master?
        </h1>
        <p className="text-xs md:text-sm text-slate-500 leading-relaxed max-w-3xl">
          Define your inquiry boundary, target rigor, and the syllabus modules you wish to defend in Socratic dialogue.
        </p>
      </div>

      {/* Pill Mode Switcher */}
      <div className="inline-flex items-center p-1 bg-slate-100 rounded-full border border-slate-200/60">
        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold transition-all ${
            activeTab === 'upload'
              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/80'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5 text-slate-500" />
          <span>Upload Document (PDF / Slides)</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('prompt')}
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold transition-all ${
            activeTab === 'prompt'
              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/80'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <span className="text-indigo-600 text-xs">✦</span>
          <span>Enter Topic Prompt</span>
        </button>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column (8 cols): Inputs & Depth & Modules */}
        <div className="lg:col-span-8 space-y-6">
          {/* Tab 1: Topic Prompt */}
          {activeTab === 'prompt' && (
            <Card className="p-6 space-y-4">
              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  Inquiry Focus & Domain
                </h2>
                <p className="text-xs text-slate-500 mb-3">
                  Enter any complex thesis, foundational discipline, or technical problem.
                </p>
                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={topicPrompt}
                    onChange={(e) => setTopicPrompt(e.target.value)}
                    placeholder="Basic Algorithms, Complexity Analysis & Sorting"
                    className="w-full pl-11 pr-4 py-3 text-sm text-slate-900 bg-white border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
                  />
                </div>
              </div>

              {/* Quick suggestion chips */}
              <div className="flex flex-wrap items-center gap-2 pt-1">
                {[
                  'Basic Algorithms & Sorting',
                  'Statistical Decision Theory',
                  'mRNA Lipid Nanoparticles',
                ].map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setTopicPrompt(chip)}
                    className="text-xs font-medium px-3.5 py-1.5 rounded-full bg-indigo-50/70 text-indigo-700 hover:bg-indigo-100 transition-colors border border-indigo-100/60"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </Card>
          )}

          {/* Tab 2: Document Upload */}
          {activeTab === 'upload' && (
            <Card className="p-6 space-y-4">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.epub,.txt,.md"
                className="hidden"
              />
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold text-slate-900">
                    Source Material Upload
                  </h2>
                  <span className="bg-indigo-50 text-indigo-700 text-[11px] font-semibold px-2 py-0.5 rounded-full">
                    Primary Ingestion
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  title="Re-upload"
                  className="text-slate-400 hover:text-slate-600 transition-colors p-1"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-slate-500">
                Provide textbook chapters, research publications, or lecture syllabi for premise extraction.
              </p>

              {/* Dropzone container */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-200 hover:border-indigo-400 rounded-2xl p-8 text-center bg-slate-50/40 hover:bg-indigo-50/20 transition-all cursor-pointer group"
              >
                <div className="w-10 h-10 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-2.5 group-hover:scale-105 transition-transform">
                  <FileUp className="w-5 h-5" />
                </div>
                <div className="text-xs font-bold text-slate-800 mb-0.5">
                  Drag & drop your syllabus, textbook PDF, or paper here
                </div>
                <div className="text-xs text-indigo-600 font-semibold hover:underline">
                  or browse files from your computer
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Supports PDF, EPUB, PPTX, or Markdown up to 50MB &bull; Optical OCR enabled
                </div>
              </div>

              {/* Parsed File Preview */}
              {uploadedFile && (
                <div className="p-3 rounded-xl border border-slate-200/90 bg-white flex items-center justify-between shadow-xs">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-orange-50 border border-orange-200 text-orange-600 flex items-center justify-center font-bold text-xs">
                      PDF
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900">
                        {uploadedFile.name}
                      </div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        {uploadedFile.size} &bull; {uploadedFile.pages} &bull; Uploaded just now
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs px-2.5 py-0.5 rounded-full font-semibold flex items-center gap-1">
                      <Check className="w-3 h-3 text-emerald-600" />
                      Parsed Successfully
                    </span>
                    <button
                      type="button"
                      onClick={() => setUploadedFile(null)}
                      className="text-slate-400 hover:text-slate-600 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </Card>
          )}

          {/* Inquiry Depth (3 Level Cards) */}
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Inquiry Depth</h2>
              <p className="text-xs text-slate-500">
                Calibrate the standard of counter-arguments and proof required during examination.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Foundation */}
              <div
                onClick={() => setSelectedDepth('foundation')}
                className={`rounded-2xl p-5 transition-all cursor-pointer flex flex-col justify-between ${
                  selectedDepth === 'foundation'
                    ? 'border-2 border-indigo-600 bg-indigo-50/40 relative shadow-xs'
                    : 'border border-slate-200/90 bg-white hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        selectedDepth === 'foundation'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <Layers className="w-5 h-5" />
                    </div>
                    {selectedDepth === 'foundation' && (
                      <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
                        ✓
                      </div>
                    )}
                  </div>
                  <h3
                    className={`text-sm font-bold mt-2 ${
                      selectedDepth === 'foundation'
                        ? 'text-indigo-950'
                        : 'text-slate-900'
                    }`}
                  >
                    Foundation
                  </h3>
                  <p
                    className={`text-xs mt-1 mb-4 leading-relaxed ${
                      selectedDepth === 'foundation'
                        ? 'text-indigo-700 font-medium'
                        : 'text-slate-500'
                    }`}
                  >
                    Core mental models, definitions, and standard examples.
                  </p>
                </div>
                <div>
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-medium inline-block ${
                      selectedDepth === 'foundation'
                        ? 'bg-indigo-900 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    3–4 hours
                  </span>
                </div>
              </div>

              {/* Applied */}
              <div
                onClick={() => setSelectedDepth('applied')}
                className={`rounded-2xl p-5 transition-all cursor-pointer flex flex-col justify-between ${
                  selectedDepth === 'applied'
                    ? 'border-2 border-indigo-600 bg-indigo-50/40 relative shadow-xs'
                    : 'border border-slate-200/90 bg-white hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        selectedDepth === 'applied'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <Cpu className="w-5 h-5" />
                    </div>
                    {selectedDepth === 'applied' && (
                      <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
                        ✓
                      </div>
                    )}
                  </div>
                  <h3
                    className={`text-sm font-bold mt-2 ${
                      selectedDepth === 'applied'
                        ? 'text-indigo-950'
                        : 'text-slate-900'
                    }`}
                  >
                    Applied
                  </h3>
                  <p
                    className={`text-xs mt-1 mb-4 leading-relaxed ${
                      selectedDepth === 'applied'
                        ? 'text-indigo-700 font-medium'
                        : 'text-slate-500'
                    }`}
                  >
                    Mechanisms, failure modes, and practical edge cases.
                  </p>
                </div>
                <div>
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-medium inline-block ${
                      selectedDepth === 'applied'
                        ? 'bg-indigo-900 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    6–8 hours
                  </span>
                </div>
              </div>

              {/* Rigorous */}
              <div
                onClick={() => setSelectedDepth('rigorous')}
                className={`rounded-2xl p-5 transition-all cursor-pointer flex flex-col justify-between ${
                  selectedDepth === 'rigorous'
                    ? 'border-2 border-indigo-600 bg-indigo-50/40 relative shadow-xs'
                    : 'border border-slate-200/90 bg-white hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div
                      className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        selectedDepth === 'rigorous'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <Shield className="w-5 h-5" />
                    </div>
                    {selectedDepth === 'rigorous' && (
                      <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
                        ✓
                      </div>
                    )}
                  </div>
                  <h3
                    className={`text-sm font-bold mt-2 ${
                      selectedDepth === 'rigorous'
                        ? 'text-indigo-950'
                        : 'text-slate-900'
                    }`}
                  >
                    Rigorous
                  </h3>
                  <p
                    className={`text-xs mt-1 mb-4 leading-relaxed ${
                      selectedDepth === 'rigorous'
                        ? 'text-indigo-700 font-medium'
                        : 'text-slate-500'
                    }`}
                  >
                    First-principles defense against adversarial probes.
                  </p>
                </div>
                <div>
                  <span
                    className={`text-xs px-3 py-1 rounded-full font-medium inline-block ${
                      selectedDepth === 'rigorous'
                        ? 'bg-indigo-900 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    12+ hours
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Curated Syllabus Modules */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  Curated Syllabus Modules
                </h2>
                <p className="text-xs text-slate-500">
                  Drag to reorder or toggle modules into your personalized roadmap.
                </p>
              </div>
              <span className="bg-slate-100 text-slate-700 text-xs px-3 py-1 font-semibold rounded-full">
                {selectedCount} modules selected
              </span>
            </div>

            <div className="bg-white border border-slate-200/80 rounded-2xl p-4 divide-y divide-slate-100 shadow-xs space-y-0">
              {modules.map((mod) => (
                <div
                  key={mod.id}
                  className="py-3.5 first:pt-1 last:pb-1 flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <GripVertical className="w-4 h-4 text-slate-300 cursor-grab shrink-0" />
                    <span className="text-xs md:text-sm font-semibold text-slate-800 truncate">
                      {mod.title}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="bg-slate-100 text-slate-600 text-xs px-2.5 py-0.5 rounded-full font-medium">
                      {mod.concepts}
                    </span>
                    <span className="text-xs text-slate-400 font-mono hidden sm:inline">
                      {mod.time}
                    </span>
                    {mod.badge === 'Recommended' && (
                      <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 text-xs px-2.5 py-0.5 rounded-full font-medium hidden md:inline">
                        Recommended
                      </span>
                    )}
                    {mod.badge === 'Optional' && (
                      <span className="bg-amber-50 text-amber-700 border border-amber-200/60 text-xs px-2.5 py-0.5 rounded-full font-medium hidden md:inline">
                        Optional
                      </span>
                    )}

                    {/* Animated iOS-style Toggle Switch / Slider */}
                    <button
                      type="button"
                      role="switch"
                      aria-checked={mod.selected}
                      onClick={() => toggleModule(mod.id)}
                      className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ease-in-out cursor-pointer ${
                        mod.selected ? 'bg-indigo-600' : 'bg-slate-200'
                      }`}
                    >
                      <div
                        className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ease-in-out ${
                          mod.selected ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (4 cols): ROADMAP SUMMARY Plan Overview */}
        <div className="lg:col-span-4">
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs space-y-5 sticky top-6">
            {/* Header */}
            <div className="space-y-1">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 font-mono">
                ROADMAP SUMMARY
              </div>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-extrabold text-slate-900">
                  Plan overview
                </h2>
                <span className="bg-indigo-50 text-indigo-700 border border-indigo-100 text-xs font-semibold px-2.5 py-0.5 rounded-full capitalize">
                  {selectedDepth} Level
                </span>
              </div>
            </div>

            {/* Metric Row 1: Active Modules */}
            <div className="bg-slate-50/80 rounded-xl p-3.5 flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-500 font-medium">
                  Active Modules
                </div>
                <div className="text-base font-bold text-slate-900 mt-0.5">
                  {selectedCount} of {modules.length}
                </div>
              </div>
              <span className="bg-emerald-50 text-emerald-700 font-bold text-[11px] px-2 py-0.5 rounded-full">
                +2 vs avg
              </span>
            </div>

            {/* Metric Row 2: Est. Inquiry Time */}
            <div className="bg-slate-50/80 rounded-xl p-3.5 flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-500 font-medium">
                  Est. Inquiry Time
                </div>
                <div className="text-base font-bold text-slate-900 mt-0.5">
                  4.8 hrs
                </div>
              </div>
              <span className="bg-slate-200/70 text-slate-700 font-medium text-[11px] px-2 py-0.5 rounded-full">
                Self-paced
              </span>
            </div>

            {/* Metric Row 3: Socratic Defenses */}
            <div className="bg-slate-50/80 rounded-xl p-3.5 flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-500 font-medium">
                  Socratic Defenses
                </div>
                <div className="text-base font-bold text-slate-900 mt-0.5">
                  3 oral exams
                </div>
              </div>
              <span className="bg-indigo-50 text-indigo-700 font-medium text-[11px] px-2 py-0.5 rounded-full">
                1:1 dialogue
              </span>
            </div>

            {/* Inquiry Distribution Segmented Bar Slider */}
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-700">
                  Inquiry Distribution
                </span>
                <span className="font-mono text-slate-500 font-medium">
                  100% Calibrated
                </span>
              </div>
              <div className="w-full h-2 rounded-full overflow-hidden flex bg-slate-100">
                <div className="w-[45%] bg-indigo-600 h-full" />
                <div className="w-[35%] bg-indigo-400 h-full" />
                <div className="w-[20%] bg-indigo-200 h-full" />
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-500 pt-0.5">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-600" />
                  45% Conceptual
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-400" />
                  35% Dialogue
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-indigo-200" />
                  20% Oral
                </span>
              </div>
            </div>

            {/* Next Socratic Checkpoint Card */}
            <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-3.5 space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-900">
                <Clock className="w-3.5 h-3.5 text-indigo-600" />
                <span>Next Socratic Checkpoint</span>
              </div>
              <p className="text-[11px] text-slate-600 leading-relaxed">
                30&ndash;min oral defense on LNP Endosomal Escape with interactive adversarial questioning.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2 pt-2">
              <Button
                variant="primary"
                size="lg"
                isLoading={isSubmitting}
                onClick={handleCommit}
                className="w-full bg-[#1e2238] hover:bg-[#151828] text-white font-bold py-3.5 rounded-xl shadow-xs"
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Build my roadmap
              </Button>
              <button
                type="button"
                onClick={() => navigate('/app/dashboard')}
                className="w-full text-center text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors py-1 block"
              >
                Save draft
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
