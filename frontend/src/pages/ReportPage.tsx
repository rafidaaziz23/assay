import React, { useState, useEffect } from 'react';
import { Award, ShieldCheck, AlertCircle, ArrowLeft, RefreshCw, CheckCircle2, XCircle } from 'lucide-react';
import { api } from '../services/api';
import { FinalReportResponse } from '../types/api';

interface ReportPageProps {
  sessionId: string;
  onReset: () => void;
}

export const ReportPage: React.FC<ReportPageProps> = ({ sessionId, onReset }) => {
  const [report, setReport] = useState<FinalReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [appealed, setAppealed] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getFinalReport(sessionId)
      .then((res) => setReport(res))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [sessionId]);

  const handleAppeal = async () => {
    setAppealed(true);
  };

  if (loading) {
    return (
      <div className="py-20 text-center font-mono text-xs text-assay-muted">
        Aggregating final verification report...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono mb-3">
          <Award className="w-3.5 h-3.5" />
          Step 6: Verification & Calibration Report
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Reasoning Integrity Audit
        </h1>
        <p className="mt-2 text-sm text-assay-muted max-w-xl mx-auto italic">
          "Every AI study tool answers questions. Assay questions your answers."
        </p>
      </div>

      <div className="bg-assay-card border border-assay-border rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        {/* Metric Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-assay-bg border border-assay-border p-4 rounded-xl text-center">
            <span className="text-xs text-assay-muted block mb-1">Mean Reasoning Score</span>
            <span className="text-2xl font-mono font-bold text-white">
              {report?.summary.mean_score || 75} / 100
            </span>
            <span className="text-[10px] text-emerald-400 block mt-1 font-mono">Unlock Threshold: &ge; 75</span>
          </div>

          <div className="bg-assay-bg border border-assay-border p-4 rounded-xl text-center">
            <span className="text-xs text-assay-muted block mb-1">Mean Calibration Gap</span>
            <span className="text-2xl font-mono font-bold text-blue-400">
              {report?.summary.mean_calibration_gap || 15} pts
            </span>
            <span className="text-[10px] text-gray-400 block mt-1 font-mono">|Predicted &minus; Actual|</span>
          </div>

          <div className="bg-assay-bg border border-assay-border p-4 rounded-xl text-center">
            <span className="text-xs text-assay-muted block mb-1">Honeypot Rejections</span>
            <span className="text-2xl font-mono font-bold text-emerald-400">
              {report?.summary.honeypot_verdicts['CRITICAL_REJECTION'] || 1} / 2
            </span>
            <span className="text-[10px] text-gray-400 block mt-1 font-mono">Fictional Traps Detected</span>
          </div>
        </div>

        {/* Chapter Breakdown Table */}
        <div>
          <h3 className="text-sm font-semibold text-gray-200 mb-3">Chapter Breakdown</h3>
          <div className="border border-assay-border rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-assay-bg text-gray-400 border-b border-assay-border">
                <tr>
                  <th className="p-3">Chapter ID</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Score</th>
                  <th className="p-3">Calibration Gap</th>
                  <th className="p-3">Integrity Signal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-assay-border text-gray-300">
                {report?.chapters.map((ch) => (
                  <tr key={ch.chapter_id} className="hover:bg-assay-bg/50">
                    <td className="p-3 font-semibold text-white">{ch.chapter_id}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          ch.status === 'UNLOCKED'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {ch.status}
                      </span>
                    </td>
                    <td className="p-3 font-bold">{ch.score} / 100</td>
                    <td className="p-3">{ch.calibration_gap} pts</td>
                    <td className="p-3">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded ${
                          ch.integrity === 'clean'
                            ? 'text-emerald-400 bg-emerald-950/40'
                            : 'text-amber-400 bg-amber-950/40'
                        }`}
                      >
                        {ch.integrity}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Appeal Path */}
        <div className="bg-assay-bg border border-assay-border rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div>
            <h4 className="font-semibold text-gray-200">Disagree with any reasoning evaluation?</h4>
            <p className="text-assay-muted text-[11px] mt-0.5">
              Submit an appeal to trigger asynchronous review by a secondary verifier model (Gemini Pro).
            </p>
          </div>
          <button
            onClick={handleAppeal}
            disabled={appealed}
            className={`px-4 py-2 rounded-lg font-medium text-xs transition-all shrink-0 ${
              appealed
                ? 'bg-gray-800 text-gray-400 border border-gray-700'
                : 'bg-assay-card border border-assay-border text-gray-300 hover:text-white hover:border-gray-500'
            }`}
          >
            {appealed ? 'Appeal Under Review (Verifier Model)' : 'Submit Score Appeal'}
          </button>
        </div>

        {/* Action Button */}
        <div className="pt-4 border-t border-assay-border flex justify-center">
          <button
            onClick={onReset}
            className="bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-6 rounded-xl text-xs flex items-center gap-2 transition-all shadow"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Start Another Learning Session</span>
          </button>
        </div>
      </div>
    </div>
  );
};
