import React from 'react';
import { ArrowRight, BookOpen, Clock, FileCheck, ExternalLink, Lock, Unlock, Shield } from 'lucide-react';
import { SyllabusResponse } from '../types/api';

interface SyllabusPageProps {
  syllabus: SyllabusResponse;
  onStartReading: (chapterId: string) => void;
}

export const SyllabusPage: React.FC<SyllabusPageProps> = ({
  syllabus,
  onStartReading,
}) => {
  const firstActiveChapter = syllabus.chapters.find((c) => c.status === 'ACTIVE_READING') || syllabus.chapters[0];

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono mb-3">
          <BookOpen className="w-3.5 h-3.5" />
          Step 3: Syllabus Synthesis
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          {syllabus.title}
        </h1>
        <div className="mt-2 flex items-center justify-center gap-3 text-xs text-assay-muted font-mono">
          <span className="bg-assay-card border border-assay-border px-2.5 py-1 rounded">
            source_mode: {syllabus.source_mode}
          </span>
          <span className="bg-assay-card border border-assay-border px-2.5 py-1 rounded">
            total_chapters: {syllabus.total_chapters}
          </span>
        </div>
      </div>

      <div className="space-y-4 mb-8">
        {syllabus.chapters.map((ch) => {
          const isLocked = ch.status === 'LOCKED';
          return (
            <div
              key={ch.chapter_id}
              className={`bg-assay-card border rounded-2xl p-6 transition-all ${
                isLocked
                  ? 'border-assay-border/50 opacity-70'
                  : 'border-blue-500/40 shadow-lg'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold font-mono shrink-0 ${
                      isLocked
                        ? 'bg-gray-800 text-gray-400 border border-gray-700'
                        : 'bg-blue-600/20 text-blue-400 border border-blue-500/50'
                    }`}
                  >
                    {ch.order}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{ch.title}</h3>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-assay-muted mt-1.5">
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        {ch.estimated_reading_minutes} mins reading
                      </span>
                      {ch.source_pages?.length > 0 && (
                        <span className="flex items-center gap-1.5 font-mono text-gray-300">
                          <FileCheck className="w-3.5 h-3.5 text-blue-400" />
                          Source Pages: [{ch.source_pages.join(', ')}]
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-end sm:self-center">
                  {isLocked ? (
                    <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-900/60 px-3 py-1.5 rounded-lg border border-gray-800">
                      <Lock className="w-3.5 h-3.5" />
                      <span>Locked (Clear Prev Ch. &ge; 75)</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => onStartReading(ch.chapter_id)}
                      className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-2 transition-all shadow"
                    >
                      <span>Study Chapter</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {ch.references?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-assay-border/60 flex flex-wrap gap-2 text-xs">
                  <span className="text-gray-500 text-[11px] uppercase tracking-wider self-center">
                    Grounded References:
                  </span>
                  {ch.references.map((ref, idx) => (
                    <div
                      key={idx}
                      className="bg-assay-bg border border-assay-border px-2.5 py-1 rounded text-gray-300 flex items-center gap-1.5 text-xs font-mono"
                    >
                      {ref.kind === 'document' ? (
                        <FileCheck className="w-3 h-3 text-emerald-400" />
                      ) : (
                        <ExternalLink className="w-3 h-3 text-blue-400" />
                      )}
                      <span>{ref.label}</span>
                      {ref.page && <span className="text-gray-500">p.{ref.page}</span>}
                      {ref.cached && (
                        <span className="text-[10px] bg-amber-500/10 text-amber-300 px-1 rounded">
                          cached
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="text-center">
        <button
          onClick={() => onStartReading(firstActiveChapter.chapter_id)}
          className="bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-8 rounded-xl text-sm inline-flex items-center gap-2 transition-all shadow-xl shadow-blue-600/20"
        >
          <span>Open Active Chapter 1</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
