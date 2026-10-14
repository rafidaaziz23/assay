"""
Deterministic Fallback & Cached Demo Engine (Zero-Crash Assurance)
Triggered by:
- ENV DEMO_MODE=cached
- Request Header 'x-demo-mode: cached'
- Runtime Gemini 429/500/503 fallback
"""
from typing import Dict, Any, List

DETERMINISTIC_ROLES = [
    "Frontend", "Backend", "Fullstack", "DevOps",
    "Data/ML", "Mobile", "QA/Test", "Security", "System Design"
]

CACHED_CHECKLIST: List[Dict[str, Any]] = [
    { "item_id": "ck_01", "topic": "Virtual DOM vs Real DOM Tree Differences", "selected": True, "confidence": 0.95, "origin": "document" },
    { "item_id": "ck_02", "topic": "Fiber Reconciler Architecture & Priority Lanes", "selected": True, "confidence": 0.91, "origin": "role_taxonomy" },
    { "item_id": "ck_03", "topic": "Concurrent Mode & Microtask State Batching", "selected": True, "confidence": 0.88, "origin": "document" },
    { "item_id": "ck_04", "topic": "Synthetic Event Pooling and Event Delegation", "selected": False, "confidence": 0.72, "origin": "grounded_external" }
]

CACHED_SYLLABUS: Dict[str, Any] = {
    "title": "Frontend Deep Dive: React Internals & Fiber Engine",
    "source_mode": "document_rag",
    "total_chapters": 3,
    "chapters": [
        {
            "chapter_id": "ch_01",
            "title": "Virtual DOM vs Real DOM: The Cost of Abstraction",
            "order": 1,
            "status": "ACTIVE_READING",
            "prerequisites": [],
            "estimated_reading_minutes": 5,
            "source_pages": [1, 2, 3],
            "references": [
                { "kind": "document", "label": "React Architecture Blueprint v18", "page": 2, "verified": True }
            ]
        },
        {
            "chapter_id": "ch_02",
            "title": "Fiber Reconciler: Priority Lanes & Scheduling",
            "order": 2,
            "status": "LOCKED",
            "prerequisites": ["ch_01"],
            "estimated_reading_minutes": 7,
            "source_pages": [4, 5, 6],
            "references": [
                { "kind": "document", "label": "React Architecture Blueprint v18", "page": 5, "verified": True },
                { "kind": "grounded_external", "label": "react.dev — Inside Fiber Reconciler", "url": "https://react.dev/blog/reconciler", "cached": True }
            ]
        },
        {
            "chapter_id": "ch_03",
            "title": "Concurrent Rendering & Interruptible Work Units",
            "order": 3,
            "status": "LOCKED",
            "prerequisites": ["ch_02"],
            "estimated_reading_minutes": 8,
            "source_pages": [7, 8, 9],
            "references": [
                { "kind": "document", "label": "React Architecture Blueprint v18", "page": 8, "verified": True }
            ]
        }
    ]
}

CHAPTER_CONTENTS: Dict[str, Dict[str, Any]] = {
    "ch_01": {
        "chapter_id": "ch_01",
        "title": "Virtual DOM vs Real DOM: The Cost of Abstraction",
        "status": "ACTIVE_READING",
        "source_pages": [1, 2, 3],
        "next_locked": True,
        "interview_available": True,
        "content_markdown": """# Chapter 1: Virtual DOM vs Real DOM: The Cost of Abstraction

The DOM (Document Object Model) is a tree-like representation of UI elements in browser memory. Manipulating the real DOM directly is expensive because modifying a node triggers browser layout recalculation and paint cycles.

React introduces the **Virtual DOM (VDOM)**, an in-memory lightweight representation of the real DOM nodes as plain JavaScript objects.

### The Reconciliation Algorithm
When state changes, React constructs a new Virtual DOM tree and diffs it against the previous tree. This diffing step operates in $O(n)$ heuristic complexity rather than the optimal $O(n^3)$ tree comparison.

Key invariants:
1. Elements of different types produce completely different subtrees.
2. The developer can hint which child elements may be stable across different renders with a stable `key` prop.

> **Active Note:** Notice that Virtual DOM does NOT mean faster than raw optimized DOM operations; its advantage lies in predictable declarative programming and batching updates.
"""
    },
    "ch_02": {
        "chapter_id": "ch_02",
        "title": "Fiber Reconciler: Priority Lanes & Scheduling",
        "status": "LOCKED",
        "source_pages": [4, 5, 6],
        "next_locked": True,
        "interview_available": False,
        "content_markdown": """# Chapter 2: Fiber Reconciler: Priority Lanes & Scheduling

React 16 replaced the old Stack Reconciler with Fiber. The Stack Reconciler was synchronous: once it started updating the component tree, it could not yield execution to the main thread until the entire tree was traversed.

Fiber structures each component as a singly linked list unit of work:
- `child`: points to first immediate child
- `sibling`: points to first immediate sibling
- `return`: points to parent fiber node

This pointer structure allows React to pause, resume, or abort work units based on priority lanes (SyncLane, InputContinuousLane, DefaultLane).
"""
    }
}
