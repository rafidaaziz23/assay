import React, { useState, useEffect } from 'react';
import { ArrowRight, CheckSquare, Square, Tag, Layers, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ChecklistItem, SyllabusResponse } from '../types/api';

interface ChecklistPageProps {
  sessionId: string;
  onChecklistCommitted: (syllabus: SyllabusResponse) => void;
}

export const ChecklistPage: React.FC<ChecklistPageProps> = ({
  sessionId,
  onChecklistCommitted,
}) => {
  const [items, setItems] = useState<ChecklistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [committing, setCommitting] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getChecklist(sessionId)
      .then((res) => {
        setItems(res.checklist);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [sessionId]);

  const toggleItem = (itemId: string) => {
    setItems((prev) =>
      prev.map((it) => (it.item_id === itemId ? { ...it, selected: !it.selected } : it))
    );
  };

  const handleCommit = async () => {
    setCommitting(true);
    try {
      const selectedIds = items.filter((it) => it.selected).map((it) => it.item_id);
      await api.updateChecklist(sessionId, selectedIds);
      const syllabus = await api.generateSyllabus(sessionId);
      onChecklistCommitted(syllabus);
    } catch (e) {
      console.error(e);
    } finally {
      setCommitting(false);
    }
  };

  const getOriginBadge = (origin: string) => {
    switch (origin) {
      case 'document':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'role_taxonomy':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'grounded_external':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      default:
        return 'bg-gray-800 text-gray-400 border-gray-700';
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-mono mb-3">
          <Layers className="w-3.5 h-3.5" />
          Step 2: Realtime Scope Checklist
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Curate Your Syllabus Scope
        </h1>
        <p className="mt-2 text-sm text-assay-muted max-w-xl mx-auto">
          Topics derived live from your intent and document. Uncheck topics you wish to skip;
          only selected items will be synthesized into chapters.
        </p>
      </div>

      <div className="bg-assay-card border border-assay-border rounded-2xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-assay-border mb-4">
          <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">
            Generated Checklist Topics
          </span>
          <span className="text-xs font-mono text-gray-400">
            {items.filter((i) => i.selected).length} of {items.length} selected
          </span>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center text-gray-400 gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
            <span className="text-xs font-mono">Streaming checklist items from Gemini pipeline...</span>
          </div>
        ) : (
          <div className="space-y-3 mb-6">
            {items.map((item) => (
              <div
                key={item.item_id}
                onClick={() => toggleItem(item.item_id)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                  item.selected
                    ? 'bg-blue-950/20 border-blue-500/50 text-white'
                    : 'bg-assay-bg/50 border-assay-border text-gray-500'
                }`}
              >
                <div className="flex items-center gap-3">
                  {item.selected ? (
                    <CheckSquare className="w-5 h-5 text-blue-400 shrink-0" />
                  ) : (
                    <Square className="w-5 h-5 text-gray-600 shrink-0" />
                  )}
                  <div>
                    <h4 className="text-sm font-medium">{item.topic}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded border font-mono ${getOriginBadge(
                          item.origin
                        )}`}
                      >
                        origin: {item.origin}
                      </span>
                      <span className="text-[10px] text-gray-500 font-mono">
                        confidence: {Math.round(item.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={handleCommit}
          disabled={committing || items.filter((i) => i.selected).length === 0}
          className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium py-3 rounded-xl text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-600/20"
        >
          <span>{committing ? 'Synthesizing Gated Syllabus...' : 'Synthesize Structured Syllabus'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
