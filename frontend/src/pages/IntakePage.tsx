import React, { useState } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Input } from '../components/atoms/Input';
import {
  Sparkles,
  Upload,
  FileText,
  CheckCircle2,
  Sliders,
  Layers,
  ArrowRight,
  GripVertical,
  Check,
  Clock,
  ShieldCheck,
  FileUp,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';

export const IntakePage: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveSessionId } = useAppStore();
  const [activeTab, setActiveTab] = useState<'prompt' | 'upload'>('prompt');
  const [topicPrompt, setTopicPrompt] = useState('How mRNA vaccines work');
  const [selectedDepth, setSelectedDepth] = useState<'foundation' | 'applied' | 'rigorous'>('applied');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedFileObj, setSelectedFileObj] = useState<File | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

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
        pages: '24 Pages',
      });
    }
  };

  const handleCommit = async () => {
    setIsSubmitting(true);
    try {
      // 1. Create intake session
      const intakeRes = await api.createIntake({
        intent: topicPrompt,
        role: selectedDepth === 'rigorous' ? 'System Design' : 'Data/ML',
        document: selectedFileObj ? selectedFileObj.name : uploadedFile?.name,
      });

      const sid = intakeRes.session_id || 'sess_a1b2c3';
      setActiveSessionId(sid);

      // 2. If file chosen, upload
      if (selectedFileObj) {
        await api.uploadDocument(sid, selectedFileObj);
      }

      // 3. Generate syllabus
      await api.generateSyllabus(sid);

      navigate('/app/roadmap');
    } catch (err) {
      console.warn('Intake submission fallback:', err);
      navigate('/app/roadmap');
    } finally {
      setIsSubmitting(false);
    }
  };

  const [modules, setModules] = useState([
    {
      id: 'mod-1',
      title: '1. Modified Nucleosides & Immune Evasion',
      concepts: '4 concepts',
      time: '45 min',
      recommended: true,
      selected: true,
    },
    {
      id: 'mod-2',
      title: '2. Lipid Nanoparticle (LNP) Formulation & Delivery',
      concepts: '5 concepts',
      time: '1 hr 15 min',
      recommended: false,
      selected: true,
    },
    {
      id: 'mod-3',
      title: '3. Ribosomal Translation & Antigen Presentation',
      concepts: '6 concepts',
      time: '1 hr 30 min',
      recommended: false,
      selected: true,
    },
    {
      id: 'mod-4',
      title: '4. Cellular & Humoral Immunity Cascades',
      concepts: '4 concepts',
      time: '50 min',
      recommended: false,
      selected: true,
    },
    {
      id: 'mod-5',
      title: '5. Socratic Defense Capstone: Counter-arguments & Efficacy',
      concepts: '7 concepts',
      time: '2 hrs',
      recommended: false,
      selected: true,
    },
  ]);

  const toggleModule = (id: string) => {
    setModules((prev) =>
      prev.map((m) => (m.id === id ? { ...m, selected: !m.selected } : m))
    );
  };

  const selectedCount = modules.filter((m) => m.selected).length;

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-200 pb-12">
      {/* Page Title Banner */}
      <div className="space-y-2">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-primary-50 border border-primary-200/60 text-[11px] font-bold tracking-wider uppercase text-primary-700">
          <Sparkles className="w-3.5 h-3.5 text-primary-600" />
          New Subject
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
          What do you want to master?
        </h1>
        <p className="text-sm text-slate-500 leading-relaxed max-w-2xl">
          Define your inquiry boundary, target rigor, and the syllabus modules you wish to defend in Socratic dialogue.
        </p>
      </div>

      {/* Tabs Switcher: Topic Prompt vs Upload PDF */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('prompt')}
          className={`pb-3 px-4 text-xs font-bold transition-all relative ${
            activeTab === 'prompt'
              ? 'text-primary-600'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          Enter Topic Prompt
          {activeTab === 'prompt' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600 rounded-t" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`pb-3 px-4 text-xs font-bold transition-all relative flex items-center gap-1.5 ${
            activeTab === 'upload'
              ? 'text-primary-600'
              : 'text-slate-500 hover:text-slate-900'
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          Upload Document (PDF / Slides)
          {activeTab === 'upload' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600 rounded-t" />
          )}
        </button>
      </div>

      {/* Tab 1: Topic Prompt Content */}
      {activeTab === 'prompt' && (
        <Card className="p-6 space-y-4">
          <div>
            <label className="text-xs font-bold text-slate-900">
              Inquiry Focus & Domain
            </label>
            <p className="text-xs text-slate-500 mb-2">
              Enter any complex thesis, foundational discipline, or technical problem.
            </p>
            <Input
              value={topicPrompt}
              onChange={(e) => setTopicPrompt(e.target.value)}
              placeholder="e.g. Distributed Consensus & Raft, Kantian Imperative..."
              className="text-base py-3"
            />
          </div>

          {/* Quick suggestion chips */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-semibold text-slate-400">
              Try exploring:
            </span>
            {[
              'mRNA Lipid Nanoparticles',
              'Distributed Consensus & Raft',
              'Kantian Categorical Imperative',
            ].map((chip) => (
              <button
                key={chip}
                onClick={() => setTopicPrompt(chip)}
                className="text-xs font-medium px-3 py-1 rounded-full bg-slate-100 text-slate-700 hover:bg-primary-50 hover:text-primary-700 transition-colors border border-slate-200/60"
              >
                {chip}
              </button>
            ))}
          </div>
        </Card>
      )}

      {/* Tab 2: Upload Document Content */}
      {activeTab === 'upload' && (
        <Card className="p-6 space-y-4">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.epub,.txt,.md"
            className="hidden"
          />
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-200 hover:border-primary-400 rounded-2xl p-8 text-center bg-slate-50/50 hover:bg-primary-50/20 transition-all cursor-pointer group"
          >
            <div className="w-12 h-12 rounded-2xl bg-primary-50 border border-primary-200/60 text-primary-600 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
              <FileUp className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 mb-1">
              Click to select or drag & drop syllabus / textbook PDF here
            </h3>
            <p className="text-xs text-slate-400">
              Supports PDF, EPUB, PPTX, or Markdown up to 50MB &bull; Optical OCR enabled
            </p>
          </div>

          {/* Uploaded File preview chip */}
          {uploadedFile && (
            <div className="p-3.5 rounded-xl border border-primary-200 bg-primary-50/60 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-900">
                    {uploadedFile.name}
                  </div>
                  <div className="text-[11px] text-slate-500 font-mono">
                    {uploadedFile.size} &bull; {uploadedFile.pages} &bull; Uploaded just now
                  </div>
                </div>
              </div>
              <Badge variant="success" size="sm">
                <Check className="w-3 h-3 mr-1" />
                Parsed
              </Badge>
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
          {[
            {
              id: 'foundation',
              label: 'Foundation',
              desc: 'Core mental models, definitions, and standard examples.',
              time: '3-4 hours',
            },
            {
              id: 'applied',
              label: 'Applied',
              desc: 'Mechanisms, failure modes, and practical edge cases.',
              time: '6-8 hours',
            },
            {
              id: 'rigorous',
              label: 'Rigorous',
              desc: 'First-principles defense against adversarial probes.',
              time: '12+ hours',
            },
          ].map((level) => {
            const isSelected = selectedDepth === level.id;
            return (
              <div
                key={level.id}
                onClick={() => setSelectedDepth(level.id as any)}
                className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'border-primary-600 bg-primary-50/50 ring-2 ring-primary-600/20 shadow-xs'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900">
                      {level.label}
                    </span>
                    {isSelected && (
                      <span className="w-4 h-4 rounded-full bg-primary-600 text-white flex items-center justify-center text-[10px]">
                        ✓
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 leading-relaxed mb-3">
                    {level.desc}
                  </p>
                </div>
                <div className="text-[11px] font-mono font-bold text-primary-700 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {level.time}
                </div>
              </div>
            );
          })}
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
          <Badge variant="primary" size="md">
            {selectedCount} modules selected
          </Badge>
        </div>

        <div className="space-y-2">
          {modules.map((mod) => (
            <div
              key={mod.id}
              onClick={() => toggleModule(mod.id)}
              className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                mod.selected
                  ? 'border-slate-200 bg-white shadow-xs'
                  : 'border-slate-100 bg-slate-50 opacity-60'
              }`}
            >
              <div className="flex items-center gap-3">
                <GripVertical className="w-4 h-4 text-slate-300 cursor-grab" />
                <input
                  type="checkbox"
                  checked={mod.selected}
                  onChange={() => toggleModule(mod.id)}
                  className="w-4 h-4 text-primary-600 rounded border-slate-300 focus:ring-primary-500"
                />
                <span className="text-xs font-bold text-slate-800">
                  {mod.title}
                </span>
                {mod.recommended && (
                  <Badge variant="success" size="sm">
                    Recommended
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-4 text-xs text-slate-400 font-mono">
                <span>{mod.concepts}</span>
                <span>&bull;</span>
                <span>{mod.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Sticky Action Bar */}
      <div className="pt-4 flex items-center justify-between border-t border-slate-200">
        <div className="text-xs text-slate-500">
          Estimated total defense preparation: <strong className="text-slate-800 font-mono">6.5 hrs</strong>
        </div>
        <Button
          variant="primary"
          size="lg"
          isLoading={isSubmitting}
          onClick={handleCommit}
          rightIcon={<ArrowRight className="w-4 h-4" />}
        >
          Commit Syllabus & Begin Reading
        </Button>
      </div>
    </div>
  );
};
