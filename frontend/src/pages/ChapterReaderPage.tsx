import React, { useState, useEffect } from 'react';
import { ArrowRight, BookOpen, Lock, Sparkles, MessageSquareQuote, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { ChapterDetailResponse, ChapterMeta } from '../types/api';
import { ChapterStepper } from '../components/ChapterStepper';
import { SocraticAskPopover } from '../components/SocraticAskPopover';

interface ChapterReaderPageProps {
  chapterId: string;
  sessionId: string;
  allChapters: ChapterMeta[];
  onSelectChapter: (id: string) => void;
  onStartInterview: (id: string) => void;
}

export const ChapterReaderPage: React.FC<ChapterReaderPageProps> = ({
  chapterId,
  sessionId,
  allChapters,
  onSelectChapter,
  onStartInterview,
}) => {
  const [chapter, setChapter] = useState<ChapterDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedText, setSelectedText] = useState('');
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [showPopover, setShowPopover] = useState(false);

  useEffect(() => {
    setLoading(true);
    setShowPopover(false);
    setSelectedText('');
    api.getChapter(chapterId)
      .then((res) => {
        setChapter(res);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [chapterId]);

  const handleMouseUp = () => {
    const selection = window.getSelection()?.toString().trim();
    if (selection && selection.length > 2) {
      setSelectedText(selection);
      setShowPopover(true);
      if (selection.split(' ').length > 1) {
        api.getSuggestions(chapterId, selection)
          .then((res) => setSuggestedQuestions(res.suggested_questions))
          .catch(() => setSuggestedQuestions([]));
      } else {
        setSuggestedQuestions([]);
      }
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center font-mono text-xs text-assay-muted">
        Loading chapter content...
      </div>
    );
  }

  if (!chapter) {
    return <div className="py-20 text-center text-red-400 text-sm">Chapter not found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Sidebar Stepper */}
      <div className="lg:col-span-1">
        <ChapterStepper
          chapters={allChapters}
          activeChapterId={chapterId}
          onSelectChapter={onSelectChapter}
        />

        <div className="mt-4 bg-assay-card border border-assay-border p-4 rounded-xl text-xs text-gray-400">
          <span className="font-semibold text-gray-200 block mb-1">Interactive Feature:</span>
          Highlight any keyword or phrase in the reading text to launch the Socratic Inquirer.
        </div>
      </div>

      {/* Main Chapter Content */}
      <div className="lg:col-span-3">
        <div className="bg-assay-card border border-assay-border rounded-2xl p-6 sm:p-8 shadow-xl">
          <div className="flex items-center justify-between pb-4 border-b border-assay-border mb-6">
            <div>
              <span className="text-xs font-mono text-blue-400 uppercase tracking-wider">
                Active Study Session
              </span>
              <h1 className="text-2xl font-bold text-white mt-1">{chapter.title}</h1>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono bg-blue-950/40 text-blue-400 border border-blue-800/40 px-2.5 py-1 rounded">
                Pages: {chapter.source_pages.join(', ')}
              </span>
            </div>
          </div>

          {/* Reader Body */}
          <div
            onMouseUp={handleMouseUp}
            className="prose prose-invert max-w-none text-gray-300 leading-relaxed text-sm space-y-4 select-text"
          >
            <div className="bg-assay-bg/60 border border-assay-border p-4 rounded-xl text-xs text-assay-muted mb-4">
              <p>
                💡 <em>Tip: Select words like <strong>reconciliation</strong> or <strong>Virtual DOM</strong> with your cursor to test the inline Socratic ask loop.</em>
              </p>
            </div>

            <div className="whitespace-pre-line font-sans text-sm text-gray-200">
              {chapter.content_markdown}
            </div>
          </div>

          {/* Popover */}
          {showPopover && (
            <div className="mt-6">
              <SocraticAskPopover
                selectedText={selectedText}
                chapterId={chapterId}
                sessionId={sessionId}
                suggestedQuestions={suggestedQuestions}
                onClose={() => setShowPopover(false)}
              />
            </div>
          )}

          {/* Navigation & Interview Gate Footer */}
          <div className="mt-8 pt-6 border-t border-assay-border flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Lock className="w-4 h-4 text-amber-500" />
              <span>Next chapter is locked until you pass the interview quiz (&ge; 75 pts).</span>
            </div>

            <button
              onClick={() => onStartInterview(chapterId)}
              className="bg-blue-600 hover:bg-blue-500 text-white font-medium px-6 py-2.5 rounded-xl text-xs flex items-center gap-2 transition-all shadow-lg shadow-blue-600/20"
            >
              <span>Begin Chapter 1 Interview Quiz</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
