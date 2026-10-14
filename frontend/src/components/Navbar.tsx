import React from 'react';
import { ShieldCheck, Flame, BookOpen, AlertCircle } from 'lucide-react';

interface NavbarProps {
  currentStep: number;
  onNavigateStep?: (step: number) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentStep, onNavigateStep }) => {
  const steps = [
    { id: 1, name: 'Intake' },
    { id: 2, name: 'Checklist' },
    { id: 3, name: 'Syllabus' },
    { id: 4, name: 'Reader' },
    { id: 5, name: 'Interview' },
    { id: 6, name: 'Report' },
  ];

  return (
    <header className="border-b border-assay-border bg-assay-card/80 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 font-bold">
            <Flame className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-white text-lg">ASSAY</span>
              <span className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded font-mono">
                Track 4: Adaptive Learning
              </span>
            </div>
            <p className="text-xs text-assay-muted hidden sm:block">Active Socratic Learning Engine — Anti-AI-Brain-Rot</p>
          </div>
        </div>

        {/* Step Navigation Pill */}
        <nav className="hidden md:flex items-center gap-1 bg-assay-bg/80 border border-assay-border p-1 rounded-full">
          {steps.map((s) => (
            <button
              key={s.id}
              onClick={() => onNavigateStep && onNavigateStep(s.id)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                currentStep === s.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : currentStep > s.id
                  ? 'text-gray-300 hover:text-white'
                  : 'text-gray-600 hover:text-gray-400'
              }`}
            >
              {s.id}. {s.name}
            </button>
          ))}
        </nav>

        {/* Resilience Mode Indicator */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2.5 py-1 rounded-md font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Zero-Crash Cache: ACTIVE</span>
            <span className="sm:hidden">CACHED</span>
          </div>
        </div>
      </div>
    </header>
  );
};
