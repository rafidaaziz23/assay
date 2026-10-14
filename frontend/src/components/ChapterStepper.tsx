import React from 'react';
import { Lock, Unlock, CheckCircle2, Clock, BookOpen } from 'lucide-react';
import { ChapterMeta } from '../types/api';

interface ChapterStepperProps {
  chapters: ChapterMeta[];
  activeChapterId: string;
  onSelectChapter: (chapterId: string) => void;
}

export const ChapterStepper: React.FC<ChapterStepperProps> = ({
  chapters,
  activeChapterId,
  onSelectChapter,
}) => {
  return (
    <div className="flex flex-col gap-2 bg-assay-card border border-assay-border p-4 rounded-xl">
      <div className="flex items-center justify-between pb-2 border-b border-assay-border">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-blue-400" />
          Syllabus Chapters
        </h3>
        <span className="text-xs font-mono text-gray-400">
          Threshold: &ge; 75 pts to unlock
        </span>
      </div>

      <div className="flex flex-col gap-2 mt-2">
        {chapters.map((ch) => {
          const isCurrent = ch.chapter_id === activeChapterId;
          const isLocked = ch.status === 'LOCKED';
          const isMastered = ch.status === 'UNLOCKED';

          return (
            <button
              key={ch.chapter_id}
              disabled={isLocked}
              onClick={() => onSelectChapter(ch.chapter_id)}
              className={`w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between ${
                isCurrent
                  ? 'bg-blue-950/40 border-blue-500/60 shadow-sm'
                  : isLocked
                  ? 'bg-assay-bg/40 border-assay-border/50 opacity-60 cursor-not-allowed'
                  : 'bg-assay-bg/70 border-assay-border hover:border-gray-500'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold font-mono ${
                    isMastered
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                      : isCurrent
                      ? 'bg-blue-500/20 text-blue-400 border border-blue-500/40'
                      : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  {isMastered ? <CheckCircle2 className="w-4 h-4" /> : ch.order}
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-200 leading-snug">{ch.title}</h4>
                  <div className="flex items-center gap-3 text-xs text-assay-muted mt-0.5">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {ch.estimated_reading_minutes} mins
                    </span>
                    {ch.source_pages?.length > 0 && (
                      <span className="font-mono">Pages: {ch.source_pages.join(', ')}</span>
                    )}
                  </div>
                </div>
              </div>

              <div>
                {isLocked ? (
                  <span className="flex items-center gap-1 text-xs text-gray-500 bg-gray-900/60 px-2.5 py-1 rounded border border-gray-800">
                    <Lock className="w-3 h-3" />
                    Locked
                  </span>
                ) : isMastered ? (
                  <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-950/30 px-2.5 py-1 rounded border border-emerald-800/40">
                    <Unlock className="w-3 h-3" />
                    Unlocked
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs text-blue-400 bg-blue-950/30 px-2.5 py-1 rounded border border-blue-800/40">
                    Active
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
