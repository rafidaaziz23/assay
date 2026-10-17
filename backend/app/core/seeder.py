"""Database seeder for Assay Socratic Engine.

Pre-populates InMemoryStore with realistic academic demonstration tracks,
chapters, Socratic anchors, and interview records on startup:
1. Coding Basic: Foundations of Algorithms & Data Structures (sess_coding_basic)
2. Math & Decision Theory: Foundations of Statistical Decision Theory (sess_math_stats & sess_a1b2c3)
"""
from __future__ import annotations

from typing import Optional
from ..repositories import InMemoryStore, get_store


def seed_store(store: Optional[InMemoryStore] = None) -> InMemoryStore:
    """Inject rich demonstration curricula into InMemoryStore if empty."""
    store = store or get_store()

    # Avoid duplicate seeding if tracks are already seeded
    if "ch_algo_01" in store.chapters and "ch_01" in store.chapters:
        return store

    # =========================================================================
    # CURRICULUM 1: CODING BASIC (ALGORITHMS & DATA STRUCTURES)
    # =========================================================================
    session_coding = "sess_coding_basic"

    store.create_session(
        session_id=session_coding,
        intent="Basic Algorithms, Complexity Analysis, Sorting, and Search Trees",
        role="Backend",
        role_is_custom=False,
        custom_role=None,
        suggested_others=False,
        has_document=False,
        document_name=None,
        source_mode="role_taxonomy_generated",
        demo_mode="live",
        status="SYLLABUS_READY",
        syllabus_id="syl_algorithms_v1",
        syllabus_title="Foundations of Algorithms & Data Structures",
    )

    checklist_coding = [
        {
            "item_id": "ck_algo_01",
            "topic": "Asymptotic Notation, Big-O Limits & Space-Time Trade-offs",
            "selected": True,
            "confidence": 0.96,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_algo_02",
            "topic": "Divide and Conquer: QuickSort, MergeSort & Recurrence Relations",
            "selected": True,
            "confidence": 0.95,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_algo_03",
            "topic": "Binary Search Invariants & Logarithmic Range Partitions",
            "selected": True,
            "confidence": 0.92,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_algo_04",
            "topic": "Hash Table Amortized Bounds & Collision Resolution",
            "selected": True,
            "confidence": 0.91,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_algo_05",
            "topic": "Graph Traversals: BFS, DFS & Topological Ordering",
            "selected": True,
            "confidence": 0.88,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_algo_06",
            "topic": "Dynamic Programming: Memoization & Optimal Substructure",
            "selected": True,
            "confidence": 0.85,
            "origin": "role_taxonomy",
        },
    ]
    store.set_checklist(session_coding, checklist_coding)

    ch_algo_01_content = """# Algorithmic Complexity and Asymptotic Analysis

Computational complexity is the study of resource consumption under scaling input sizes $n$. When analyzing algorithms, we abstract machine-dependent constants by formulating asymptotic bounds.

## 1. Asymptotic Bounds & Formal Definitions

A function $f(n)$ is in $\mathcal{O}(g(n))$ if there exist positive constants $c$ and $n_0$ such that:

$$0 \le f(n) \le c \cdot g(n) \quad \text{for all } n \ge n_0$$

Conversely, $\Omega(g(n))$ defines the asymptotic lower bound, and $\Theta(g(n))$ defines a tight bound where $f(n)$ is sandwiched between $c_1 \cdot g(n)$ and $c_2 \cdot g(n)$.

```python
def binary_search(arr: list[int], target: int) -> int:
    # Time Complexity: O(log n)
    # Space Complexity: O(1) auxiliary
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

## 2. The Recurrence Relation & Master Theorem

For divide-and-conquer algorithms with recurrence $T(n) = a T(n/b) + f(n)$, the Master Theorem provides the asymptotic upper bound by comparing $f(n)$ to $n^{\log_b a}$.

In comparison-based sorting, any decision tree algorithm requires height $h \ge \log_2(n!) = \Omega(n \log n)$. Hence, no comparison sort can break the comparison sort lower bound in the worst case.

## 3. Space Complexity & Call Stack Memory

Space complexity accounts for both auxiliary memory allocations and the recursive execution call stack. A recursive function with recursion depth $d$ allocates $\mathcal{O}(d)$ stack frames in memory until leaf termination.
"""

    store.put_chapter({
        "chapter_id": "ch_algo_01",
        "session_id": session_coding,
        "title": "Algorithmic Complexity & Big-O Notation",
        "order": 1,
        "status": "ACTIVE_READING",
        "next_locked": True,
        "reading_time_minutes": 18,
        "objectives": [
            "Formulate asymptotic upper bound O(g(n)) and tight bound Theta(g(n))",
            "Analyze divide-and-conquer recurrences using the Master Theorem",
            "Prove the Omega(n log n) comparison-based sorting lower bound",
        ],
        "source_pages": [1, 2, 3],
        "content_markdown": ch_algo_01_content,
        "references": [
            {
                "ref_id": "ref_algo_01",
                "title": "Introduction to Algorithms (4th Edition)",
                "authors": "Cormen, Leiserson, Rivest, Stein (CLRS)",
                "page": 1,
                "verified": True,
            },
            {
                "ref_id": "ref_algo_02",
                "title": "The Design and Analysis of Computer Algorithms",
                "authors": "Aho, Hopcroft, Ullman",
                "page": 2,
                "verified": True,
            },
        ],
    })

    store.put_chapter({
        "chapter_id": "ch_algo_02",
        "session_id": session_coding,
        "title": "Divide and Conquer: QuickSort & MergeSort",
        "order": 2,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 22,
        "objectives": [
            "Derive average-case O(n log n) and worst-case O(n^2) for QuickSort",
            "Analyze cache-locality and stability trade-offs in MergeSort",
        ],
        "source_pages": [4, 5],
        "content_markdown": "Chapter locked until Chapter 1 oral defense is verified.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_algo_03",
        "session_id": session_coding,
        "title": "Binary Search & Logarithmic Bounds",
        "order": 3,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 15,
        "objectives": [
            "Formalize loop invariants in binary search ranges",
            "Apply bisection methods to monotonic predicate functions",
        ],
        "source_pages": [6],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_algo_04",
        "session_id": session_coding,
        "title": "Hash Tables & Collision Resolution",
        "order": 4,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 20,
        "objectives": [
            "Analyze expected O(1) lookups under simple uniform hashing",
            "Compare chaining against open addressing and robin-hood hashing",
        ],
        "source_pages": [7, 8],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_algo_05",
        "session_id": session_coding,
        "title": "Graph Traversals: BFS, DFS & Shortest Paths",
        "order": 5,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 25,
        "objectives": [
            "Implement topological sort using Kahn's algorithm and DFS timestamps",
            "Prove correctness of Dijkstra's algorithm with non-negative edge weights",
        ],
        "source_pages": [9, 10],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_algo_06",
        "session_id": session_coding,
        "title": "Dynamic Programming & Optimal Substructure",
        "order": 6,
        "status": "LOCKED",
        "next_locked": False,
        "reading_time_minutes": 30,
        "objectives": [
            "Identify overlapping subproblems and state transition recurrence",
            "Perform space-optimization on DP tables",
        ],
        "source_pages": [11, 12],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    # Oral Interview for Coding Basic Chapter 1
    store.create_interview(
        interview_id="intv_demo_algo_01",
        chapter_id="ch_algo_01",
        session_id=session_coding,
        turn_index=1,
        injected_term="Quantum QuickSort",
        first_question=(
            "Candidate Lin. In analyzing algorithm complexity, suppose an engineer claims that "
            "their sorting routine achieves O(1) worst-case time by leveraging Quantum QuickSort. "
            "Is this claim mathematically valid under the comparison-based model, or does a "
            "fundamental computational lower bound exist?"
        ),
        honeypot_metadata={
            "injected_term": "Quantum QuickSort",
            "origin": "fictional_term",
            "expected_action": "CRITICAL_REJECTION",
        },
    )

    # =========================================================================
    # CURRICULUM 2: MATH & STATISTICAL DECISION THEORY
    # =========================================================================
    session_math = "sess_math_stats"

    # Also register sess_a1b2c3 for full backward compatibility with legacy tests
    for s_id in (session_math, "sess_a1b2c3"):
        store.create_session(
            session_id=s_id,
            intent="Decision Theory, Neyman-Pearson Lemma, and Likelihood Ratio Bounds",
            role="Data/ML",
            role_is_custom=False,
            custom_role=None,
            suggested_others=False,
            has_document=True,
            document_name="Statistical_Inference_and_Optimal_Testing.pdf",
            source_mode="document_rag",
            demo_mode="live",
            status="SYLLABUS_READY",
            syllabus_id="syl_decision_theory_v1",
            syllabus_title="Foundations of Statistical Decision Theory & Causal Rigor",
        )

    checklist_math = [
        {
            "item_id": "ck_01",
            "topic": "Likelihood Ratio Tests & Monotone Probability Densities",
            "selected": True,
            "confidence": 0.95,
            "origin": "document",
        },
        {
            "item_id": "ck_02",
            "topic": "Neyman–Pearson Lemma & Uniformly Most Powerful (UMP) Boundary",
            "selected": True,
            "confidence": 0.98,
            "origin": "document",
        },
        {
            "item_id": "ck_03",
            "topic": "Causal DAGs, Backdoor Adjustment & Residual Confounding",
            "selected": True,
            "confidence": 0.92,
            "origin": "document",
        },
        {
            "item_id": "ck_04",
            "topic": "Maximum Likelihood Estimation & Asymptotic Normality",
            "selected": True,
            "confidence": 0.89,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_05",
            "topic": "Bayesian Decision Rules & Minimaxity",
            "selected": True,
            "confidence": 0.86,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_06",
            "topic": "Algorithmic Information & Kolmogorov Descriptive Bounds",
            "selected": True,
            "confidence": 0.84,
            "origin": "role_taxonomy",
        },
    ]
    store.set_checklist(session_math, checklist_math)
    store.set_checklist("sess_a1b2c3", checklist_math)

    ch_01_content = """# The Fundamental Lemma of Hypothesis Testing

In standard decision theoretic protocols, the central paradox of empirical observation resides in the unobserved counterfactual: what would have transpired had the treatment not been assigned? In standard randomized controlled protocols, balance secures exchangeability in expectation.

However, when comparing simple hypotheses $H_0: \theta = \theta_0$ versus $H_1: \theta = \theta_1$, the Neyman-Pearson lemma demonstrates that the likelihood ratio test statistic:

$$\Lambda(x) = \frac{L(\theta_0 \mid x)}{L(\theta_1 \mid x)} \le k$$

is mathematically optimal. It achieves maximum statistical power while strictly bounding the Type I error rate at significance level $\alpha$.

Sample independence guarantees that the composite random vector produces a product measure over the sample space. Under classical regularity conditions, when observations $X_1, \dots, X_n$ are drawn independently from parameterized distribution $f(x; \theta)$, the joint likelihood factors cleanly, guaranteeing the monotone likelihood ratio property holds uniformly.
"""

    store.put_chapter({
        "chapter_id": "ch_01",
        "session_id": "sess_a1b2c3",
        "title": "Statistics for Decisions: Neyman–Pearson Lemma",
        "order": 1,
        "status": "ACTIVE_READING",
        "next_locked": True,
        "reading_time_minutes": 15,
        "objectives": [
            "Formulate the Neyman-Pearson lemma from first principles",
            "Derive the optimal likelihood ratio threshold k",
            "Demonstrate why UMP tests depend on monotone likelihood ratio",
        ],
        "source_pages": [1, 2, 3],
        "content_markdown": ch_01_content,
        "references": [
            {
                "ref_id": "ref_np_01",
                "title": "On the Problem of the most Efficient Tests of Statistical Hypotheses",
                "authors": "J. Neyman, E. S. Pearson (1933)",
                "page": 1,
                "verified": True,
            },
            {
                "ref_id": "ref_np_02",
                "title": "Testing Statistical Hypotheses (3rd Edition)",
                "authors": "E. L. Lehmann, Joseph P. Romano",
                "page": 2,
                "verified": True,
            },
        ],
    })

    store.put_chapter({
        "chapter_id": "ch_02",
        "session_id": "sess_a1b2c3",
        "title": "Causal Inference & Potential Outcomes",
        "order": 2,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 20,
        "objectives": [
            "Formalize the Backdoor Criterion on directed acyclic graphs",
            "Prove non-identifiability under unobserved confounding",
            "Derive instrumental variable estimators in two-stage least squares",
        ],
        "source_pages": [4, 5, 6],
        "content_markdown": "Chapter 2 content is locked until Chapter 1 oral defense is completed.",
        "references": [
            {
                "ref_id": "ref_causal_01",
                "title": "Causality: Models, Reasoning, and Inference",
                "authors": "Judea Pearl (Cambridge University Press)",
                "page": 4,
                "verified": True,
            }
        ],
    })

    store.put_chapter({
        "chapter_id": "ch_03",
        "session_id": "sess_a1b2c3",
        "title": "Maximum Likelihood & Score Equations",
        "order": 3,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 22,
        "objectives": [
            "Compute Fisher Information matrices and Cramer-Rao bounds",
            "Prove asymptotic efficiency of maximum likelihood estimators",
        ],
        "source_pages": [7, 8],
        "content_markdown": "Chapter 3 content is locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_04",
        "session_id": "sess_a1b2c3",
        "title": "Confidence Intervals & Duality with Testing",
        "order": 4,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 18,
        "objectives": [
            "Invert acceptance regions of UMP tests to construct optimal confidence sets",
        ],
        "source_pages": [9, 10],
        "content_markdown": "Chapter 4 content is locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_05",
        "session_id": "sess_a1b2c3",
        "title": "Bayesian Decision Rules & Loss Functions",
        "order": 5,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 25,
        "objectives": [
            "Derive Bayes risk and posterior expected loss",
            "Show minimaxity under least favorable prior distributions",
        ],
        "source_pages": [11, 12],
        "content_markdown": "Chapter 5 content is locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_06",
        "session_id": "sess_a1b2c3",
        "title": "Epistemology of Artificial Reason & Counter-Examples",
        "order": 6,
        "status": "LOCKED",
        "next_locked": False,
        "reading_time_minutes": 25,
        "objectives": [
            "Differentiate inductive pattern completion from deductive validity",
            "Construct formal counter-examples to deceptive model premises",
        ],
        "source_pages": [13, 14],
        "content_markdown": "Chapter 6 content is locked.",
        "references": [],
    })

    # Oral Interview for Statistics Chapter 1
    store.create_interview(
        interview_id="intv_demo_01",
        chapter_id="ch_01",
        session_id="sess_a1b2c3",
        turn_index=1,
        injected_term="Quantum Bayesian Shrinkage",
        first_question=(
            "Candidate Lin. In evaluating the Neyman-Pearson lemma, suppose an analyst claims "
            "that increasing the significance level alpha from 0.05 to 0.10 will simultaneously "
            "reduce Type II error beta and widen the critical region without altering the power curve slope. "
            "Is this logically consistent, or does an unstated trade-off exist?"
        ),
        honeypot_metadata={
            "injected_term": "Quantum Bayesian Shrinkage",
            "origin": "fictional_term",
            "expected_action": "CRITICAL_REJECTION",
        },
    )

    return store
