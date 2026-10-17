import { useState, useEffect, useRef, useCallback } from 'react';

// SpeechRecognition window interface
interface IWindow extends Window {
  webkitSpeechRecognition?: any;
  SpeechRecognition?: any;
}

export function useVoiceDefense(onTranscriptChange?: (text: string) => void) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [waveformBars, setWaveformBars] = useState<number[]>(
    Array.from({ length: 24 }, () => 18)
  );

  const isListeningRef = useRef(false);
  const recognitionRef = useRef<any>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const fallbackIntervalRef = useRef<any>(null);
  const onTranscriptChangeRef = useRef(onTranscriptChange);

  useEffect(() => {
    onTranscriptChangeRef.current = onTranscriptChange;
  }, [onTranscriptChange]);

  const stopWaveformVisualizer = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current);
      fallbackIntervalRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch (_) {}
      });
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current) {
      try {
        if (audioContextRef.current.state !== 'closed') {
          audioContextRef.current.close().catch(() => {});
        }
      } catch (_) {}
      audioContextRef.current = null;
    }
    setWaveformBars(Array.from({ length: 24 }, () => 18));
  }, []);

  const stopListening = useCallback(() => {
    isListeningRef.current = false;
    setIsListening(false);
    stopWaveformVisualizer();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        try {
          recognitionRef.current.abort();
        } catch (_) {}
      }
    }
  }, [stopWaveformVisualizer]);

  // Initialize SpeechRecognition once
  useEffect(() => {
    const win = window as unknown as IWindow;
    const SpeechRecognitionClass =
      win.SpeechRecognition || win.webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      setIsSupported(false);
      return;
    }

    try {
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      // Auto-detect browser language or fall back to English
      recognition.lang = navigator.language || 'en-US';

      recognition.onresult = (event: any) => {
        let current = '';
        for (let i = 0; i < event.results.length; i++) {
          current += event.results[i][0].transcript;
        }
        setTranscript(current);
        if (onTranscriptChangeRef.current) {
          onTranscriptChangeRef.current(current);
        }
      };

      recognition.onerror = (err: any) => {
        console.warn('[Assay Voice] Speech recognition event:', err?.error || err);
        // Do not force stop on non-fatal speech errors like 'no-speech'
        if (err?.error === 'not-allowed' || err?.error === 'service-not-allowed') {
          stopListening();
        }
      };

      recognition.onend = () => {
        // If the user is still supposed to be listening, auto-restart speech recognition if possible
        if (isListeningRef.current) {
          try {
            recognition.start();
          } catch (_) {
            // Cannot restart; stop gracefully
            stopListening();
          }
        } else {
          stopListening();
        }
      };

      recognitionRef.current = recognition;
    } catch (err) {
      console.warn('[Assay Voice] Could not initialize SpeechRecognition:', err);
      setIsSupported(false);
    }

    return () => {
      isListeningRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (_) {}
      }
      stopWaveformVisualizer();
    };
  }, [stopListening, stopWaveformVisualizer]);

  const startWaveformVisualizer = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      const audioCtx = new AudioContextClass();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateBars = () => {
        if (!isListeningRef.current || !analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);

        const bars: number[] = [];
        for (let i = 0; i < 24; i++) {
          const val = dataArray[i % bufferLength] || 0;
          bars.push(Math.max(15, Math.min(95, (val / 255) * 100)));
        }
        setWaveformBars(bars);
        animationFrameRef.current = requestAnimationFrame(updateBars);
      };

      updateBars();
    } catch (e) {
      console.warn('[Assay Voice] Mic stream access error, using simulated waveform:', e);
      // Fallback: animated pseudo waveform
      if (fallbackIntervalRef.current) clearInterval(fallbackIntervalRef.current);
      fallbackIntervalRef.current = setInterval(() => {
        if (!isListeningRef.current) return;
        setWaveformBars(
          Array.from({ length: 24 }, () => Math.floor(Math.random() * 70) + 20)
        );
      }, 100);
    }
  }, []);

  const startListening = useCallback(async () => {
    isListeningRef.current = true;
    setIsListening(true);
    setTranscript('');

    await startWaveformVisualizer();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        // Recognition might already be running
      }
    }
  }, [startWaveformVisualizer]);

  const toggleListening = useCallback(() => {
    if (isListeningRef.current) {
      stopListening();
    } else {
      startListening();
    }
  }, [startListening, stopListening]);

  return {
    isListening,
    transcript,
    setTranscript,
    isSupported,
    waveformBars,
    startListening,
    stopListening,
    toggleListening,
  };
}
