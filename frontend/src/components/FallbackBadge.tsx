import React from 'react';
import { Database, ShieldAlert } from 'lucide-react';

export const FallbackBadge: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border border-amber-600/30 text-amber-300 text-xs px-3 py-1.5 rounded-lg flex items-center justify-between gap-3 mb-6 font-mono">
      <div className="flex items-center gap-2">
        <Database className="w-4 h-4 text-amber-400" />
        <span><strong>LOCAL_DETERMINISTIC_CACHE</strong>: Zero-crash fallback scenario engaged.</span>
      </div>
      <span className="text-[10px] bg-amber-500/20 text-amber-200 px-2 py-0.5 rounded uppercase tracking-wider font-semibold">
        DEMO-SAFE
      </span>
    </div>
  );
};
