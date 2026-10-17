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

  const recognitionRef = useRef<any>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    const win = window as unknown as IWindow;
    const SpeechRecognitionClass =
      win.SpeechRecognition || win.webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      setIsSupported(false);
      return;
    }

    const recognition = new SpeechRecognitionClass();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let current = '';
      for (let i = 0; i < event.results.length; i++) {
        current += event.results[i][0].transcript;
      }
      setTranscript(current);
      if (onTranscriptChange) {
        onTranscriptChange(current);
      }
    };

    recognition.onerror = (err: any) => {
      console.warn('[Assay Voice] Speech error:', err);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [onTranscriptChange]);

  const startWaveformVisualizer = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const audioCtx = new (window.AudioContext ||
        (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateBars = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);

        const bars: number[] = [];
        for (let i = 0; i < 24; i++) {
          const val = dataArray[i % bufferLength] || 0;
          // Scale to 15% - 95%
          bars.push(Math.max(15, Math.min(95, (val / 255) * 100)));
        }
        setWaveformBars(bars);
        animationFrameRef.current = requestAnimationFrame(updateBars);
      };

      updateBars();
    } catch (e) {
      console.warn('[Assay Voice] Mic stream access error, using simulated waveform:', e);
      // Fallback: animated pseudo waveform
      const interval = setInterval(() => {
        setWaveformBars(
          Array.from({ length: 24 }, () => Math.floor(Math.random() * 80) + 15)
        );
      }, 100);
      (mediaStreamRef as any).fallbackInterval = interval;
    }
  }, []);

  const stopWaveformVisualizer = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if ((mediaStreamRef as any)?.fallbackInterval) {
      clearInterval((mediaStreamRef as any).fallbackInterval);
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setWaveformBars(Array.from({ length: 24 }, () => 18));
  }, []);

  const startListening = useCallback(async () => {
    setTranscript('');
    setIsListening(true);
    await startWaveformVisualizer();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        // Already started
      }
    }
  }, [startWaveformVisualizer]);

  const stopListening = useCallback(() => {
    setIsListening(false);
    stopWaveformVisualizer();

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // Stopped
      }
    }
  }, [stopWaveformVisualizer]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

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
