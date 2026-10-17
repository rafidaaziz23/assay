---
name: assay-spec-driven-design
description: >-
  Standardized guidelines and extraction procedures for translating Assay Figma frames
  into pixel-perfect React 18 + TypeScript + Tailwind CSS components. Enforces atomic
  design hierarchy, design token usage, and strict accessibility.
---

# Assay Spec-Driven Design (SDD) Skill

This skill enforces pixel-perfect alignment with the approved Figma designs for **Assay: Active Socratic Learning Engine** (AI Builder Cup 2026).

---

## 1. Design DNA & Tokens

- **Typography**: `Plus Jakarta Sans` (weights: 400 Regular, 500 Medium, 600 SemiBold, 700 Bold, 800 ExtraBold).
- **Core Color Ramp**:
  - `primary`: `#4F46E5` (Indigo-600)
  - `primary-hover`: `#4338CA` (Indigo-700)
  - `primary-surface`: `#EEF0FF` (Periwinkle soft background)
  - `slate-900`: `#0F172A` (Headings, primary text)
  - `slate-700`: `#334155` (Body text)
  - `slate-500`: `#64748B` (Muted labels, secondary icons)
  - `slate-200`: `#E2E8F0` (Card borders, dividers)
  - `slate-50`: `#F8FAFC` (App background)
  - `white`: `#FFFFFF` (Surface cards)
- **Status & Socratic Feedback**:
  - `success`: `#10B981` (Mastered / Passed Defense)
  - `warning`: `#F59E0B` (Needs Elaboration / Bloom Probing)
  - `danger`: `#EF4444` (Fallacy Flagged / Socratic Challenge)
  - `info`: `#06B6D4` (Active Chapter Reading)

---

## 2. Atomic Component Hierarchy

Strict separation of concerns must be maintained:
1. `src/components/atoms/`: Indivisible UI elements (`Button`, `Input`, `Badge`, `Avatar`, `Card`). No domain logic.
2. `src/components/molecules/`: Compositions of atoms (`SearchInput`, `MetricPill`, `Breadcrumbs`, `AudioLevelIndicator`).
3. `src/components/organisms/`: Self-contained complex sections (`AppSidebar`, `AppHeader`, `WaveformVisualizer`, `SocraticReader`, `RubricScorecard`).
4. `src/layouts/`: Shell wrappers (`AppLayout`, `AuthLayout`).
5. `src/pages/`: Screen routes binding state and organisms.

---

## 3. Auto-Layout Translation Rules

When parsing Figma layout properties:
- `HORIZONTAL` auto-layout with `SPACE_BETWEEN` → `flex flex-row items-center justify-between`
- `VERTICAL` auto-layout with `itemSpacing: 16` → `flex flex-col gap-4`
- `paddingLeft: 24, paddingRight: 24` → `px-6`
- `cornerRadius: 12` → `rounded-xl`
- `cornerRadius: 9999` → `rounded-full`
- Never hardcode arbitrary pixel dimensions like `w-[317px]` if a responsive token or percentage flex applies.
