import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { FallbackBadge } from './components/FallbackBadge';
import { IntakePage } from './pages/IntakePage';
import { ChecklistPage } from './pages/ChecklistPage';
import { SyllabusPage } from './pages/SyllabusPage';
import { ChapterReaderPage } from './pages/ChapterReaderPage';
import { InterviewQuizPage } from './pages/InterviewQuizPage';
import { ReportPage } from './pages/ReportPage';

import { IntakeResponse, SyllabusResponse, ChapterMeta } from './types/api';

export function App() {
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [sessionId, setSessionId] = useState<string>('sess_a1b2c3');
  const [syllabus, setSyllabus] = useState<SyllabusResponse | null>(null);
  const [activeChapterId, setActiveChapterId] = useState<string>('ch_01');

  // Sample initial chapters
  const [chapters, setChapters] = useState<ChapterMeta[]>([
    {
      chapter_id: 'ch_01',
      title: 'Virtual DOM vs Real DOM',
      order: 1,
      status: 'ACTIVE_READING',
      prerequisites: [],
      estimated_reading_minutes: 4,
      source_pages: [3, 4, 5],
      references: [
        { kind: 'document', label: 'Uploaded PDF', page: 4, verified: true }
      ]
    },
    {
      chapter_id: 'ch_02',
      title: 'Fiber Reconciler & Scheduling',
      order: 2,
      status: 'LOCKED',
      prerequisites: ['ch_01'],
      estimated_reading_minutes: 6,
      source_pages: [6, 7, 8],
      references: [
        { kind: 'document', label: 'Uploaded PDF', page: 7, verified: true },
        { kind: 'grounded_external', label: 'react.dev — Reconciler', url: 'https://react.dev/', cached: true }
      ]
    }
  ]);

  const handleIntakeComplete = (res: IntakeResponse) => {
    setSessionId(res.session_id);
    setCurrentStep(2);
  };

  const handleChecklistCommitted = (sylRes: SyllabusResponse) => {
    setSyllabus(sylRes);
    if (sylRes.chapters?.length > 0) {
      setChapters(sylRes.chapters);
      setActiveChapterId(sylRes.chapters[0].chapter_id);
    }
    setCurrentStep(3);
  };

  const handleStartReading = (chapterId: string) => {
    setActiveChapterId(chapterId);
    setCurrentStep(4);
  };

  const handleStartInterview = (chapterId: string) => {
    setActiveChapterId(chapterId);
    setCurrentStep(5);
  };

  const handleInterviewPassed = () => {
    // Unlock chapter 2
    setChapters((prev) =>
      prev.map((c) =>
        c.chapter_id === 'ch_01'
          ? { ...c, status: 'UNLOCKED' }
          : c.chapter_id === 'ch_02'
          ? { ...c, status: 'ACTIVE_READING' }
          : c
      )
    );
    setCurrentStep(6);
  };

  const handleReset = () => {
    setCurrentStep(1);
  };

  return (
    <div className="min-h-screen bg-assay-bg text-assay-text flex flex-col font-sans">
      <Navbar currentStep={currentStep} onNavigateStep={(step) => setCurrentStep(step)} />

      <main className="flex-1 pb-16">
        <div className="max-w-6xl mx-auto px-4 pt-4">
          <FallbackBadge />

          {currentStep === 1 && (
            <IntakePage onIntakeComplete={handleIntakeComplete} />
          )}

          {currentStep === 2 && (
            <ChecklistPage
              sessionId={sessionId}
              onChecklistCommitted={handleChecklistCommitted}
            />
          )}

          {currentStep === 3 && syllabus && (
            <SyllabusPage
              syllabus={syllabus}
              onStartReading={handleStartReading}
            />
          )}

          {currentStep === 4 && (
            <ChapterReaderPage
              chapterId={activeChapterId}
              sessionId={sessionId}
              allChapters={chapters}
              onSelectChapter={(id) => setActiveChapterId(id)}
              onStartInterview={handleStartInterview}
            />
          )}

          {currentStep === 5 && (
            <InterviewQuizPage
              chapterId={activeChapterId}
              sessionId={sessionId}
              onInterviewPassed={handleInterviewPassed}
            />
          )}

          {currentStep === 6 && (
            <ReportPage sessionId={sessionId} onReset={handleReset} />
          )}
        </div>
      </main>

      <footer className="border-t border-assay-border py-6 text-center text-xs text-assay-muted font-mono">
        Assay: The Active Socratic Learning Engine &bull; AI Builder Cup 2026 (Track 4: Adaptive Learning) &bull; Hard Deadline: 18 Oct 2026
      </footer>
    </div>
  );
}

export default App;
