# End-to-End User Flow & Screen Progression
## CogniForge: Active Socratic Learning Engine

This document defines the entire user journey, from first opening the platform to completing a learning module, including the UI interactions, the state machine behind the scenes, and the branching.

---

## 1. Visual Diagram: The Complete User Flow

```mermaid
flowchart TD
    Start([User Enters Platform]) --> Choice{Select Entry Mode}
    Choice -->|Upload Document| Upload[Upload PDF / Paste Module Text]
    Choice -->|Quick Demo / Judges| Preset[Pick Pre-loaded Topic: React Internals]

    Upload --> Chunking[AI splits material into 3 Nodes in the Skill Tree]
    Preset --> Chunking

    Chunking --> Dashboard[Dashboard: Open Skill Tree DAG]
    Dashboard --> ClickNode[User Clicks Node 1: Status ACTIVE_READING]

    subgraph Phase1 [Phase 1: Active Reading & Gatekeeping]
        ClickNode --> ReadingView[Limited Reading View, 300-500 words]
        ReadingView --> LockNotice['Next / Done' Button Locked]
        ReadingView --> FeynmanGate[Feynman Synthesis Form:<br/>Explain this concept in 2-3 sentences in your own words]
        FeynmanGate --> SubmitGate[User Clicks 'Open Interrogation Session']
        SubmitGate --> GateEval{Does the Summary Pass?}
        GateEval -- No / Lacking Substance --> RetryGate[Show Evaluator Feedback & Revise]
        RetryGate --> FeynmanGate
    end

    GateEval -- Yes / Pass --> Phase2

    subgraph Phase2 [Phase 2: Dynamic Socratic Interrogation & Honeypot]
        Phase2[Open Socratic Terminal Window]
        Phase2 --> Round1[AI Poses a Real-World Case Reasoning Question]
        Round1 --> UserAnswer1[User Types a Reasoning Answer]
        UserAnswer1 --> AdaptiveFollowUp[AI Analyzes & Presses with a Follow-up]

        AdaptiveFollowUp --> HoneypotInjection[AI Inserts a Fictional Concept / Honeypot Trap<br/>Example: 'React Quantum Hook']
        HoneypotInjection --> UserResponseChoice{User Response to the Honeypot}

        UserResponseChoice -->|Trap 1: Copies External AI| CheaterBranch[User pastes an explanation from ChatGPT/Claude]
        UserResponseChoice -->|Trap 2: Critical / Understands| CriticalBranch[User rejects it: 'This concept is fictional / does not exist']
        UserResponseChoice -->|Trap 3: Guesswork / Unsure| GuessBranch[User makes up an answer with no basis]

        CheaterBranch --> RedAlert[RED POP-UP: AI Hallucination Copypaste Detected!<br/>Score: 0 / 100]
        CriticalBranch --> GreenBonus[GREEN BADGE: Critical Thinker Verified!<br/>Reasoning Score: 100 / 100]
        GuessBranch --> WarningScore[Low Reasoning Score: 20-40 / 100]
    end

    RedAlert --> NodeEvaluation
    GreenBonus --> NodeEvaluation
    WarningScore --> NodeEvaluation

    subgraph Phase3 [Phase 3: Scoring & Node Unlock]
        NodeEvaluation{Is the Combined Score >= 75?}
        NodeEvaluation -- Fail --> LockedFail[Node Stays Yellow/Red: Remedial Required]
        LockedFail --> ReadingView

        NodeEvaluation -- Pass --> UnlockSuccess[Node 1 Turns GREEN / MASTERED]
        UnlockSuccess --> UnlockNext[Node 2 Opens / UNLOCKED]
        UnlockNext --> RadarUpdate[Dual-Metric Scorecard Updated:<br/>Concept Mastery vs Critical Resilience]
    end

    RadarUpdate --> NextAction{Keep Learning?}
    NextAction -- Yes --> ClickNode2[User Clicks Node 2]
    NextAction -- No --> Certificate[View Reasoning Transcript & Finish]
```

---

## 2. Detailed Step-by-Step Breakdown (Step-by-Step UI Experience)

Here is what the **user sees, feels, and does on screen**:

### Step 1: Landing & Module Selection
1. The user opens the app at `https://cogniforge.run.app`.
2. They are presented with two options:
   * **Button A (Custom Ingestion):** *Drag & drop* their own module PDF or paste syllabus text.
   * **Button B (Instant Demo Mode — For Judges):** one click on *"Load Demo: React Internals & Virtual DOM"* so judges can test immediately without hunting for a PDF.

### Step 2: Skill Tree Visualization (Skill Tree Dashboard)
1. Once the material is processed (only 1-2 seconds via Gemini 2.5 Flash), a tree graph (*DAG*) appears:
   * **Node 1 (Foundation):** **Yellow (In Progress / Active)**.
   * **Node 2 & Node 3:** **Grey (Locked)** with a padlock icon 🔒.
2. The user clicks **Node 1** to start learning.

### Step 3: Active Reading & Gatekeeping (No Instant Summaries!)
1. The screen splits in two (*split-screen*):
   * **Left side:** condensed reading text for Node 1 (300–500 words).
   * **Right side:** active verification panel.
2. **There is no "Summarize Document" button**.
3. At the bottom of the right side there is an input box:
   > *"Explain the core concept on the left in your own words (Feynman Technique), as if you were explaining it to a junior programmer."*
4. The **"Start Exam Session"** button is greyed out and cannot be clicked until the user types at least 20 words of original explanation.

### Step 4: Socratic Interrogation Session (Dynamic Interview)
1. When the initial summary is submitted and judged plausible by the AI, the interface switches to the **Socratic Interrogation Terminal**.
2. **Turn 1 (Real-World Case Trigger):**
   * The AI does not ask for rote definitions, but poses a scenario:
     > *"If you have 10,000 list items updated every 100ms, where does the Virtual DOM actually become a performance bottleneck compared to direct DOM manipulation?"*
   * The user types their argument.
3. **Turn 2 (Adaptive Probe):**
   * The AI analyzes the user's answer and presses on the consequences:
     > *"Good analysis. If VDOM burns CPU cycles during diffing, why doesn't React use direct fine-grained reactivity like Svelte or SolidJS?"*

### Step 5: THE CLIMAX MOMENT — Honeypot Question Injection (Honeypot Trap)
Mid-conversation (Turn 2 or 3), the AI subtly injects a fictional concept:
> *"Then how about the implementation of **'React Quantum Hook'**? Can that feature eliminate the state reconciliation overhead?"*

This is where 2 dramatic branches prove learning integrity:

* **Scenario A (The Cheating User / ChatGPT Copy-Paste):**
  1. The user copies the question and throws it into ChatGPT in another tab.
  2. ChatGPT (given the LLM tendency to please the asker) fabricates a long explanation: *"React Quantum Hook is an experimental hook in React that leverages quantum state bundling..."*
  3. The user pastes ChatGPT's text into CogniForge.
  4. **RED ALARM FIRES ON SCREEN:**
     ```
┌────────────────────────────────────────────────────────────┐
│  [!] AI HALLUCINATION COPYPASTE DETECTED                   │
│  The term "React Quantum Hook" is a fictional concept!     │
│  You were detected using an external AI without            │
│  critical verification. Reasoning Score: 0 / 100           │
└────────────────────────────────────────────────────────────┘
     ```
     The system records the incident and locks the node's completion.

* **Scenario B (The Critical User Who Reads Independently):**
  1. The user answers:
     > *"As far as I know, 'React Quantum Hook' never existed in React. What exists is useTransition or useDeferredValue."*
  2. **GREEN NOTIFICATION APPEARS:**
     ```
┌────────────────────────────────────────────────────────────┐
│  [✓] CRITICAL THINKER CONFIRMED                            │
│  You successfully detected and rejected a false premise!   │
│  Critical Reasoning Score: 100 / 100                       │
└────────────────────────────────────────────────────────────┘
     ```

### Step 6: Unlocking & Final Score Calculation
1. The interview session ends. The screen shows the **Dual-Metric Mastery Card**:
   * **Concept Mastery Score:** 92% (accuracy of understanding the core material).
   * **Critical Reasoning Score:** 100% (resistance to traps & quality of logic).
2. If the combined score is $\ge 75\%$:
   * **Node 1 turns GREEN (Mastered)** with an animation.
   * The padlock icon on **Node 2 opens (UNLOCKED)**.
   * The user is ready to move on to the next level!

---

## 3. User Action vs System Response Matrix

| User Action | CogniForge System Response | Pedagogical / Technical Purpose |
|---|---|---|
| Looking for an instant summary button | Button is unavailable; instructions ask the user to read the material | Forces *active reading* (SQ3R). |
| Pasting long text from outside | `paste_detected: true` recorded in telemetry | Detects the absence of manual typing. |
| Answering correctly but briefly | AI presses with a follow-up: *"Why is that so?"* | Tests the depth of the *reasoning trace*. |
| Swallowing the Honeypot wholesale | Shows a red alert and gives a score of 0 on the critical aspect | Penalizes lazy dependence on external AI. |
| Dismantling the Honeypot term | Awards maximum points and unlocks the next module | Rewards reasoning power and originality of thought. |