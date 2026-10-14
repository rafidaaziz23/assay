import React, { useState } from 'react';
import { Target, Award, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { CalibrationResponse } from '../types/api';

interface CalibrationSliderProps {
  chapterId: string;
  interviewId: string;
  onCalibrationComplete: (res: CalibrationResponse) => void;
}

export const CalibrationSlider: React.FC<CalibrationSliderProps> = ({
  chapterId,
  interviewId,
  onCalibrationComplete,
}) => {
  const [predictedScore, setPredictedScore] = useState(85);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await api.submitCalibration(chapterId, interviewId, predictedScore);
      onCalibrationComplete(res);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-assay-card border border-blue-500/30 rounded-xl p-5 shadow-lg text-gray-200">
      <div className="flex items-center gap-2 mb-2 text-blue-400 font-semibold">
        <Target className="w-5 h-5" />
        <h3 className="text-base font-semibold">Self-Calibration: Predict Before Reveal</h3>
      </div>
      <p className="text-xs text-assay-muted mb-4 leading-relaxed">
        Before we compute your final score, estimate your actual mastery (0–100).
        Assay measures the <strong>Calibration Gap</strong> (|predicted &minus; actual|) to detect overconfidence and illusory competence.
      </p>

      <div className="bg-assay-bg border border-assay-border p-4 rounded-lg mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-assay-muted">Predicted Mastery Score:</span>
          <span className="text-lg font-mono font-bold text-blue-400">{predictedScore} / 100</span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={predictedScore}
          onChange={(e) => setPredictedScore(Number(e.target.value))}
          className="w-full h-2 bg-assay-border rounded-lg appearance-none cursor-pointer accent-blue-500"
        />
        <div className="flex justify-between text-[10px] text-gray-500 mt-1 font-mono">
          <span>0 (Complete Uncertainty)</span>
          <span>50 (Moderate)</span>
          <span>100 (Mastery)</span>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={submitting}
        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 rounded-lg text-xs flex items-center justify-center gap-2 transition-all shadow"
      >
        <span>{submitting ? 'Calculating Calibration...' : 'Lock Prediction & Reveal Actual Score'}</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
};
