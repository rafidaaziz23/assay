import React, { useState, useEffect } from 'react';
import { Camera, Eye, Users, AlertTriangle, ShieldCheck, EyeOff } from 'lucide-react';

interface FocusModeMonitorProps {
  onIntegrityChange?: (flag: string, autoBlur: boolean) => void;
  autoBlurActive: boolean;
}

export const FocusModeMonitor: React.FC<FocusModeMonitorProps> = ({
  onIntegrityChange,
  autoBlurActive,
}) => {
  const [accessibleMode, setAccessibleMode] = useState(false);
  const [cameraActive, setCameraActive] = useState(true);
  const [detectedFaces, setDetectedFaces] = useState(1);
  const [gazeDrift, setGazeDrift] = useState(false);

  // Trigger test events for hackathon demo
  const simulateDrift = () => {
    setGazeDrift(true);
    if (onIntegrityChange) {
      onIntegrityChange('assisted', true);
    }
    setTimeout(() => {
      setGazeDrift(false);
      if (onIntegrityChange) {
        onIntegrityChange('clean', false);
      }
    }, 4000);
  };

  const simulateMultipleFaces = () => {
    setDetectedFaces(2);
    if (onIntegrityChange) {
      onIntegrityChange('assisted', true);
    }
    setTimeout(() => {
      setDetectedFaces(1);
      if (onIntegrityChange) {
        onIntegrityChange('clean', false);
      }
    }, 4000);
  };

  const toggleAccessibleMode = () => {
    const next = !accessibleMode;
    setAccessibleMode(next);
    if (next) {
      setCameraActive(false);
      if (onIntegrityChange) {
        onIntegrityChange('assisted_unverified', false);
      }
    } else {
      setCameraActive(true);
      if (onIntegrityChange) {
        onIntegrityChange('clean', false);
      }
    }
  };

  return (
    <div className="bg-assay-card border border-assay-border rounded-xl p-4 text-xs text-gray-300">
      <div className="flex items-center justify-between pb-2 border-b border-assay-border mb-3">
        <div className="flex items-center gap-2 font-semibold text-gray-200">
          <Camera className="w-4 h-4 text-blue-400" />
          <span>Focus Mode (On-Device ML)</span>
        </div>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded">
          video_transmitted: false
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-assay-bg border border-assay-border p-2 rounded flex items-center justify-between">
          <span className="text-assay-muted flex items-center gap-1.5">
            <Eye className="w-3.5 h-3.5 text-blue-400" />
            Gaze Status:
          </span>
          <span className={`font-mono font-medium ${gazeDrift ? 'text-amber-400' : 'text-emerald-400'}`}>
            {gazeDrift ? 'DRIFT DETECTED' : 'FOCUSED'}
          </span>
        </div>

        <div className="bg-assay-bg border border-assay-border p-2 rounded flex items-center justify-between">
          <span className="text-assay-muted flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-blue-400" />
            Faces:
          </span>
          <span className={`font-mono font-medium ${detectedFaces > 1 ? 'text-red-400' : 'text-emerald-400'}`}>
            {detectedFaces} detected
          </span>
        </div>
      </div>

      {autoBlurActive && (
        <div className="mb-3 bg-red-950/50 border border-red-500/50 p-2.5 rounded-lg flex items-center gap-2 text-red-200">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <div>
            <strong className="block text-xs font-semibold">Integrity Signal Triggered</strong>
            <span className="text-[11px] text-red-300">Auto-blur engaged to preserve exam validity.</span>
          </div>
        </div>
      )}

      {/* Accessible Mode & Test Trigger Buttons */}
      <div className="flex items-center justify-between pt-2 border-t border-assay-border mt-2">
        <button
          onClick={toggleAccessibleMode}
          className={`text-[11px] px-2.5 py-1 rounded border transition-all flex items-center gap-1.5 ${
            accessibleMode
              ? 'bg-amber-950/40 border-amber-500/40 text-amber-300'
              : 'bg-assay-bg border-assay-border text-gray-400 hover:text-white'
          }`}
        >
          <EyeOff className="w-3.5 h-3.5" />
          <span>Accessible Mode: {accessibleMode ? 'ON' : 'OFF'}</span>
        </button>

        <div className="flex gap-1.5">
          <button
            onClick={simulateDrift}
            className="text-[10px] bg-assay-bg hover:bg-assay-border px-2 py-1 rounded text-gray-400 hover:text-gray-200"
          >
            Simulate Drift
          </button>
          <button
            onClick={simulateMultipleFaces}
            className="text-[10px] bg-assay-bg hover:bg-assay-border px-2 py-1 rounded text-gray-400 hover:text-gray-200"
          >
            Simulate 2 Faces
          </button>
        </div>
      </div>
    </div>
  );
};
