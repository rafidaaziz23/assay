# Assay - Planner & Specification Hub

Dokumen ini adalah pusat perencanaan eksekusi berbasis **Spec-Driven Development (SDD)** untuk platform **Assay** (Active Socratic Learning Engine).

---

## 📌 Context & Foundation
- **Product Name**: Assay
- **Target Event**: AI Builder Cup 2026
- **Architecture**:
  - **Backend**: FastAPI, LiteLLM / Gemini 2.5 Flash, SQLite / PostgreSQL, Socratic Engine (`assay/backend`)
  - **Frontend**: Vite + React 18 + TypeScript + Tailwind CSS (`assay/frontend`)
  - **AI & Eval Pipeline**: Socratic Examiner, Bloom Taxonomy Rubric, Audio STT/TTS (`assay/ai`, `assay/eval`)
- **Approved Figma Design**:
  - File Key: `ZBHideTw5iEKgSbOLuRYmF`
  - URL: [Figma File Assay](https://www.figma.com/design/ZBHideTw5iEKgSbOLuRYmF/Assay?node-id=0-1&t=4hpHb1QoCtA6Ginh-1)
  - Total Approved Frames: 14 Frames (Trenning V2 Design System DNA)

---

## 🎯 Master Goals & Deliverables
1. **Frontend Modernization**: Slicing dan implementasi 14 frame dari Figma ke komponen React + Tailwind CSS secara presisi (1:1 visual fidelity).
2. **Design Tokens & UI Kit**: Ekstraksi token warna, border radius, bayangan halus, dan tipografi Plus Jakarta Sans ke dalam `tailwind.config.js` dan komponen atomik.
3. **End-to-End User Flow**:
   - Authentication (Login/Register)
   - Dual-mode Intake (Prompt manual & PDF upload parsing)
   - Syllabus roadmap & module curation
   - Socratic reader dengan text-highlight explanation popover
   - Real-time oral defense dengan audio waveform & rubric scoring
   - Competency dossier report & analytics export
   - Learner profile & personal settings
   - Guided onboarding tour & notification flyout

---

## 📋 Execution Roadmap (Sprint Backlog)
*Detail spesifikasi agen, skill yang dibutuhkan, goals per tahap, dan tracking history akan diperbarui secara komprehensif berdasarkan prompt arsitektur dari Claude.*

| Phase | Milestone | Scope | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Design Tokens & Atoms | Konfigurasi Tailwind, Plus Jakarta Sans, Lucide icons, button variants, pill chips | ✅ Complete |
| **Phase 2** | Core Learning Flow | Intake (Upload + Manual), Roadmap Curation, Deep Reader + Popover | ✅ Complete |
| **Phase 3** | Oral Defense & Exam | Socratic live audio examiner, waveform visualizer, dynamic rubric scoring | ✅ Complete |
| **Phase 4** | Platform Features | Dashboard, Profile, Settings, Onboarding Tour, Notification Flyout | ✅ Complete |
| **Phase 5** | Dossier & Export | Competency analytics, radar spider chart, PDF export, integration testing | ✅ Complete (UI Ready) |

---

## 📜 Execution History
- **2026-10-17**: Inisiasi `planner.md` dan verifikasi 14 frame approved dari Figma Assay.
- **2026-10-17**: Implementasi SDD Infrastructure:
  - Custom Workspace Skills terpasang (`assay-spec-driven-design`, `assay-audio-socratic`, `assay-visual-qa`).
  - Runtime Subagents terdaftar (`design-system-architect`, `component-slicer`, `state-and-audio-engineer`, `qa-visual-auditor`).
  - Ekstraksi token dari frame `1:2650` (Plus Jakarta Sans, Indigo `#4F46E5`, Periwinkle `#EEF0FF`).
  - Slicing 14 screen approved Figma ke React 18 + TS + Tailwind CSS.
  - Verifikasi build `npm.cmd run build` selesai 100% hijau (Exit Code 0).

## Claude Prompt

```
You are an AI assistant (Claude) tasked with generating a **Spec‑Driven Development execution plan** for the *Assay* project based on the provided planning document.

### Agent Roles & Hand‑off Rules
- **Orchestrator** – owns the overall planner, sequences phases, logs execution, never writes component code directly.
- **Design‑System‑Architect** – extracts design tokens from Figma node `1:2650`, creates `tailwind.config.ts`, `src/styles/tokens.css`, exports icons as React components.
- **Component‑Slicer** – slices each approved Figma frame into atoms, molecules, organisms, builds pages, provides Storybook demos under `/_kit`.
- **State‑And‑Audio‑Engineer** – sets up Zustand stores, mock API layer, Web Audio capture, Socratic markdown parser.
- **QA‑Visual‑Auditor** – runs visual regression against Figma screenshots, performs a11y checks, logs defects.
- **Integration‑Engineer** – swaps mock services for real FastAPI backend, validates contracts.

### Required Skills (must be available)
1. **Figma Node Extraction** – fetch node metadata, SVG export via Figma MCP.
2. **Tailwind Token Configuration** – map colors, fonts, spacing, radii to `theme.extend` with CSS variables.
3. **React 18 + TS Architecture** – strict typing, atomic hierarchy, forwardRef, polymorphic `as` props.
4. **Web Audio API** – MediaRecorder, analyser, waveform visualiser, reduced‑motion fallback.
5. **Markdown Socratic Parser** – unified + remark plugins, safe rendering.
6. **Mock API / Zustand** – seed data, latency simulation, Zod validation.
7. **Accessible Popovers** – Floating UI / Radix, focus management.
8. **Visual Regression & A11y QA** – Playwright screenshots (1440 px / 390 px), axe‑core scans.

### Phase Milestones
| Phase | Goal | Deliverables |
|------|------|--------------|
| **Phase 1** | Design Tokens & Atoms | Tailwind config, token CSS, icons, atom components (`Button`, `IconButton`, `Input`, `Tag`). |
| **Phase 2** | Core Learning Flow | Pages: Login, Register, Sidebar (hover state), Onboarding tour, Upload PDF page, Manual prompt entry, Roadmap curation. |
| **Phase 3** | Oral Defense & Exam | Audio capture component, waveform visualiser, rubric UI, exam state machine. |
| **Phase 4** | Platform Features | Dashboard, Profile, Settings, Notification flyout, guided tour enhancements. |
| **Phase 5** | Dossier & Export | Analytics radar chart, PDF export, final visual QA report. |

### Execution Log Template (append to this file under each phase)
```
### Execution Log – Phase X
- **Start**: <timestamp>
- **Agents Invoked**: <list>
- **Key Decisions**: <bullet list>
- **Deviations Register**: <if any>
- **Status**: ⏳ Pending / ✅ Done / ❌ Blocked
- **Next Steps**: <bullet list>
```

### Direct Prompt for Claude (trigger Phase 1 automatically)
```
Generate a full Spec‑Driven Development specification for **Phase 1** of the *Assay* project.
Include:
1. Detailed token extraction plan for node `1:2650` (colors, radii, spacing, typography, shadows).
2. Tailwind `theme.extend` configuration file content.
3. List of SVG icons to export, with filenames and React component skeletons.
4. Atom component list with prop interfaces and visual states.
5. Any token deviations from Figma (log them in the Deviation Register).
6. Handoff note from **Orchestrator** → **Design‑System‑Architect**.
Output must be valid markdown that can be directly pasted into `planner.md` under the appropriate sections.
```
```
--- End of Prompt ---
```
