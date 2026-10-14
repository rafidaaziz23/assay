import React, { useState, useEffect } from 'react';
import { ArrowRight, FileText, Upload, Sparkles, Check, HelpCircle } from 'lucide-react';
import { api } from '../services/api';
import { IntakeResponse } from '../types/api';

interface IntakePageProps {
  onIntakeComplete: (res: IntakeResponse) => void;
}

export const IntakePage: React.FC<IntakePageProps> = ({ onIntakeComplete }) => {
  const [intent, setIntent] = useState('I want to understand how React rendering works internally');
  const [selectedRole, setSelectedRole] = useState('Frontend');
  const [roles, setRoles] = useState<string[]>([
    'Frontend', 'Backend', 'Fullstack', 'DevOps',
    'Data/ML', 'Mobile', 'QA/Test', 'Security', 'System Design'
  ]);
  const [customRole, setCustomRole] = useState('');
  const [hasFile, setHasFile] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getRoles()
      .then((res) => {
        if (res.roles) setRoles(res.roles);
      })
      .catch((err) => console.warn('Using default seed roles:', err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (intent.trim().split(' ').length < 3) {
      setError('Please provide at least 3 words describing your learning intent.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const isCustom = selectedRole === 'Others';
      const res = await api.createIntake({
        intent,
        role: isCustom ? customRole || 'Custom' : selectedRole,
        role_is_custom: isCustom,
        custom_role: isCustom ? customRole : undefined,
        document: hasFile ? fileName : null
      });
      onIntakeComplete(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to submit intake');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          Step 1: Pedagogical Intake
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          What do you want to master today?
        </h1>
        <p className="mt-2 text-sm text-assay-muted max-w-xl mx-auto">
          Assay is a high-friction Socratic engine. There is <strong>no instant summary button</strong>.
          You define the intent; Assay interrogates your reasoning.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-assay-card border border-assay-border rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        {/* Intent Field */}
        <div>
          <label className="block text-xs font-semibold text-gray-200 uppercase tracking-wider mb-2">
            1. Learning Intent (Free-Text)
          </label>
          <textarea
            rows={3}
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="e.g. I want to understand how React rendering works internally and why Virtual DOM diffing has performance tradeoffs"
            className="w-full bg-assay-bg border border-assay-border rounded-xl p-3.5 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Role Selector */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-gray-200 uppercase tracking-wider">
              2. Target Role Taxonomy (Seed List)
            </label>
            <span className="text-[11px] text-assay-muted">ADR 004: Role Seed + Auto Others</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {roles.map((r) => (
              <button
                type="button"
                key={r}
                onClick={() => setSelectedRole(r)}
                className={`py-2 px-3 rounded-lg border text-xs font-medium transition-all text-left flex items-center justify-between ${
                  selectedRole === r
                    ? 'bg-blue-600/20 border-blue-500 text-white shadow-sm'
                    : 'bg-assay-bg border-assay-border text-gray-400 hover:border-gray-500'
                }`}
              >
                <span>{r}</span>
                {selectedRole === r && <Check className="w-3.5 h-3.5 text-blue-400" />}
              </button>
            ))}
            <button
              type="button"
              onClick={() => setSelectedRole('Others')}
              className={`py-2 px-3 rounded-lg border text-xs font-medium transition-all text-left flex items-center justify-between ${
                selectedRole === 'Others'
                  ? 'bg-blue-600/20 border-blue-500 text-white'
                  : 'bg-assay-bg border-assay-border text-gray-400 hover:border-gray-500'
              }`}
            >
              <span>Others</span>
              {selectedRole === 'Others' && <Check className="w-3.5 h-3.5 text-blue-400" />}
            </button>
          </div>

          {selectedRole === 'Others' && (
            <div className="mt-3">
              <input
                type="text"
                value={customRole}
                onChange={(e) => setCustomRole(e.target.value)}
                placeholder="Specify your custom role (e.g. Distributed Database Architect)..."
                className="w-full bg-assay-bg border border-assay-border rounded-lg px-3.5 py-2 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* Optional Document Upload */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-semibold text-gray-200 uppercase tracking-wider">
              3. Supporting Document (Optional)
            </label>
            <span className="text-[11px] text-emerald-400 font-mono">No document works too</span>
          </div>

          <div
            onClick={() => {
              setHasFile(!hasFile);
              setFileName(!hasFile ? 'React-Fiber-Architecture-Blueprint.pdf' : null);
            }}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
              hasFile
                ? 'border-emerald-500/50 bg-emerald-950/10'
                : 'border-assay-border hover:border-gray-500 bg-assay-bg/50'
            }`}
          >
            {hasFile ? (
              <div className="flex items-center justify-center gap-2 text-emerald-400 text-xs font-medium">
                <FileText className="w-4 h-4" />
                <span>{fileName} (Attached)</span>
                <span className="text-[10px] text-gray-400 ml-2">(Click to remove)</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-1.5 text-gray-400">
                <Upload className="w-6 h-6 text-gray-500" />
                <span className="text-xs">Click to attach sample PDF (or leave blank to generate from Role Taxonomy)</span>
                <span className="text-[10px] text-assay-muted">PDF-RAG anchors claims to specific page numbers</span>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-950/40 border border-red-500/40 rounded-lg text-xs text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-3 rounded-xl text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
        >
          <span>{loading ? 'Synthesizing Topic Scope...' : 'Proceed to Realtime Checklist'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
