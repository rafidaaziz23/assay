import React, { useState } from 'react';
import { HelpCircle, Sparkles, Send, CornerDownRight, X, ShieldAlert } from 'lucide-react';
import { api } from '../services/api';
import { SocraticAskResponse } from '../types/api';

interface SocraticAskPopoverProps {
  selectedText: string;
  chapterId: string;
  sessionId: string;
  suggestedQuestions?: string[];
  onClose: () => void;
}

export const SocraticAskPopover: React.FC<SocraticAskPopoverProps> = ({
  selectedText,
  chapterId,
  sessionId,
  suggestedQuestions = [],
  onClose,
}) => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<SocraticAskResponse | null>(null);

  const handleAsk = async (qText: string) => {
    if (!qText.trim()) return;
    setLoading(true);
    try {
      const res = await api.socraticAsk(chapterId, {
        session_id: sessionId,
        selected_text: selectedText,
        question: qText,
      });
      setResponse(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-assay-card border border-blue-500/40 rounded-xl p-4 shadow-2xl max-w-lg w-full text-sm text-gray-200 mt-4">
      <div className="flex items-center justify-between pb-2 border-b border-assay-border mb-3">
        <div className="flex items-center gap-2 text-blue-400 font-semibold">
          <Sparkles className="w-4 h-4" />
          <span>Socratic Inquirer</span>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white p-1 rounded hover:bg-assay-bg"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="mb-3">
        <span className="text-xs text-assay-muted">Selected text:</span>
        <div className="bg-assay-bg border border-assay-border p-2 rounded text-xs font-mono text-blue-300 mt-1">
          "{selectedText}"
        </div>
      </div>

      {suggestedQuestions.length > 0 && !response && (
        <div className="mb-3">
          <span className="text-xs text-assay-muted block mb-1">Suggested inquiries:</span>
          <div className="flex flex-col gap-1.5">
            {suggestedQuestions.map((sq, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuestion(sq);
                  handleAsk(sq);
                }}
                className="text-left text-xs bg-assay-bg/80 hover:bg-blue-950/40 hover:border-blue-500/40 border border-assay-border p-2 rounded text-gray-300 transition-all flex items-start gap-1.5"
              >
                <CornerDownRight className="w-3.5 h-3.5 text-blue-400 mt-0.5 shrink-0" />
                <span>{sq}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {!response && (
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAsk(question)}
            placeholder="What does this mechanism actually do?"
            className="flex-1 bg-assay-bg border border-assay-border rounded-lg px-3 py-2 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => handleAsk(question)}
            disabled={loading || !question.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-3 py-2 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{loading ? 'Thinking...' : 'Interrogate'}</span>
          </button>
        </div>
      )}

      {response && (
        <div className="mt-3 bg-assay-bg/90 border border-assay-border rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
              Assay Socratic Counter-Question
            </span>
            <span className="text-[10px] bg-red-500/10 border border-red-500/30 text-red-300 px-2 py-0.5 rounded font-mono font-medium">
              gave_direct_answer: false
            </span>
          </div>

          <p className="text-xs text-gray-300 leading-relaxed italic mb-3">
            "{response.reply}"
          </p>

          {response.citations?.length > 0 && (
            <div className="text-[11px] text-assay-muted flex items-center gap-1 pt-2 border-t border-assay-border/60">
              <span className="font-mono">Reference anchor: Page {response.citations[0].page}</span>
            </div>
          )}

          <button
            onClick={() => {
              setResponse(null);
              setQuestion('');
            }}
            className="mt-3 w-full text-center text-xs text-blue-400 hover:underline"
          >
            Ask another inquiry
          </button>
        </div>
      )}
    </div>
  );
};
