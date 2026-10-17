---
name: assay-audio-socratic
description: >-
  Architectural patterns and implementation instructions for Web Audio API waveform visualizers,
  real-time microphone capture, Socratic markdown text highlighting, and Bloom Taxonomy probe state machines.
---

# Assay Audio & Socratic Engine Skill

This skill governs the interactive oral defense and Socratic reading experiences in Assay.

---

## 1. Web Audio API & Waveform Visualization

- **Microphone Stream**: Request audio via `navigator.mediaDevices.getUserMedia({ audio: true })`.
- **Analyser Node**:
  - Connect to `AudioContext.createAnalyser()`.
  - Set `fftSize = 256` or `512` for responsive time-domain data.
  - Sample with `analyser.getByteTimeDomainData(dataArray)`.
- **Canvas Rendering**:
  - Scale canvas buffer for `window.devicePixelRatio` to prevent blurry lines on Retina displays.
  - Render smooth rounded bars or sinusoidal curves using primary Indigo (`#4F46E5`).
  - Respect `prefers-reduced-motion` media query by replacing dynamic oscillations with a static meter.
- **Teardown & Memory Management**:
  - Always call `stream.getTracks().forEach(track => track.stop())` on component unmount.
  - Suspend or close `AudioContext` to avoid audio resource leaks.

---

## 2. Socratic Reader & Highlight Mechanism

- **AST-Based Highlights**:
  - Parse Socratic text markers: `==text to probe==` or `[[concept::explanation]]`.
  - Render clickable span with custom background `bg-indigo-50 text-indigo-700 border-b-2 border-indigo-500 font-medium cursor-pointer`.
- **Popover Behavior**:
  - Render explanation dialog using collision-aware floating positioning.
  - Support instant "Ask Socratic Tutor" button that triggers an automated follow-up question.
  - Keyboard accessible: `Escape` closes, focus returns to highlight span.
