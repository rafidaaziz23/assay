---
name: assay-visual-qa
description: >-
  Visual regression, accessibility verification, and quality assurance auditing procedures
  for Assay against the approved Figma frames.
---

# Assay Visual & Accessibility QA Skill

This skill outlines the quality criteria and auditing workflow for verifying sliced React components against the 14 approved Figma frames in file `ZBHideTw5iEKgSbOLuRYmF`.

---

## 1. Defect Severity Scale

- **S1 (Blocker)**: Broken layout preventing page interaction, missing mandatory UI elements from Figma, JavaScript/runtime crash.
- **S2 (Major)**: Token divergence (e.g., incorrect primary colors, incorrect font family, missing hover/focus state on interactive elements), misalignment exceeding 8px.
- **S3 (Polish)**: Minor spacing nuances (< 4px), subtle shadow gradient differences, icon stroke width variations.

---

## 2. Accessibility & Quality Checklist

1. **Keyboard Reachability**: All buttons, links, tabs, and popovers must be focusable via `Tab` with visible focus rings (`focus-visible:ring-2 focus-visible:ring-indigo-500`).
2. **Color Contrast**: Text on background must meet WCAG AA minimum 4.5:1 ratio (`#0F172A` on `#FFFFFF` and `#F8FAFC`, `#FFFFFF` on `#4F46E5`).
3. **Empty & Loading States**:
   - Every list or data view must support loading skeleton or spinner and empty placeholder illustrations.
4. **Clean Code & Strict TypeScript**:
   - Zero `any` types.
   - Clean prop interfaces documented with JSDoc where needed.
