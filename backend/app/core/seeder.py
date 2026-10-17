"""Database seeder for Assay Socratic Engine.

Pre-populates the persistent store with 360° demonstration data:
1. Users: Maya Lin (Fellow), Dr. Julian Vance (Examiner), Prof. Elena Rostova (Scientist), Alex Rivera (Scholar)
2. Curricula:
   - Track 1: Coding Basic / Algorithms & Data Structures (sess_coding_basic, 6 chapters)
   - Track 2: Math & Statistical Decision Theory (sess_math_stats & sess_a1b2c3, 6 chapters)
   - Track 3: Distributed Systems & Consensus Protocols (sess_dist_systems, 5 chapters)
3. Socratic Dialectic Inquiries (6 records)
4. Interactive Notifications & Alerts (5 items)
5. Upcoming Oral Defenses & Examiners (3 schedules)
"""
from __future__ import annotations

import sys
from typing import Optional
from ..repositories import InMemoryStore, get_store


def seed_store(store: Optional[InMemoryStore] = None) -> InMemoryStore:
    """Inject complete demonstration data into store."""
    store = store or get_store()

    # =========================================================================
    # 1. SEED USERS (LEARNERS & FACULTY EXAMINERS)
    # =========================================================================
    users_data = [
        {
            "id": "usr_rafida",
            "name": "Rafida Aziz",
            "email": "rafida.aziz@gmail.com",
            "role": "Lead Fellow · Socratic Scholar",
            "handle": "@rafidaaziz",
            "institution": "University Research Scholar",
            "streak_days": 21,
            "credits": 2500,
            "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
        },
        {
            "id": "usr_mayalin",
            "name": "Maya Lin",
            "email": "maya.lin@stanford.edu",
            "role": "Fellow",
            "handle": "@mayalin",
            "institution": "Stanford University",
            "streak_days": 14,
            "credits": 1250,
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
        },
        {
            "id": "usr_julian",
            "name": "Dr. Julian Vance",
            "email": "j.vance@oxford.ac.uk",
            "role": "Lead Examiner · Decision Theory",
            "handle": "@julianvance",
            "institution": "Oxford University",
            "streak_days": 42,
            "credits": 3400,
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
        },
        {
            "id": "usr_elena",
            "name": "Prof. Elena Rostova",
            "email": "e.rostova@mit.edu",
            "role": "Principal Scientist · Distributed Systems",
            "handle": "@erostova",
            "institution": "MIT CSAIL",
            "streak_days": 28,
            "credits": 2800,
            "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
        },
        {
            "id": "usr_alex",
            "name": "Alex Rivera",
            "email": "alex.rivera@berkeley.edu",
            "role": "Graduate Scholar",
            "handle": "@arivera",
            "institution": "UC Berkeley",
            "streak_days": 7,
            "credits": 850,
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80",
        },
    ]
    for u in users_data:
        store.save_user(u)

    # =========================================================================
    # 2. CURRICULUM 1: CODING BASIC (ALGORITHMS & DATA STRUCTURES)
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

A function $f(n)$ is in $\\mathcal{O}(g(n))$ if there exist positive constants $c$ and $n_0$ such that:

$$0 \\le f(n) \\le c \\cdot g(n) \\quad \\text{for all } n \\ge n_0$$

Conversely, $\\Omega(g(n))$ defines the asymptotic lower bound, and $\\Theta(g(n))$ defines a tight bound where $f(n)$ is sandwiched between $c_1 \\cdot g(n)$ and $c_2 \\cdot g(n)$.

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

For divide-and-conquer algorithms with recurrence $T(n) = a T(n/b) + f(n)$, the Master Theorem provides the asymptotic upper bound by comparing $f(n)$ to $n^{\\log_b a}$.

In comparison-based sorting, any decision tree algorithm requires height $h \\ge \\log_2(n!) = \\Omega(n \\log n)$. Hence, no comparison sort can break the comparison sort lower bound in the worst case.

## 3. Space Complexity & Call Stack Memory

Space complexity accounts for both auxiliary memory allocations and the recursive execution call stack. A recursive function with recursion depth $d$ allocates $\\mathcal{O}(d)$ stack frames in memory until leaf termination.
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
    # 3. CURRICULUM 2: MATH & STATISTICAL DECISION THEORY
    # =========================================================================
    session_math = "sess_math_stats"

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

However, when comparing simple hypotheses $H_0: \\theta = \\theta_0$ versus $H_1: \\theta = \\theta_1$, the Neyman-Pearson lemma demonstrates that the likelihood ratio test statistic:

$$\\Lambda(x) = \\frac{L(\\theta_0 \\mid x)}{L(\\theta_1 \\mid x)} \\le k$$

is mathematically optimal. It achieves maximum statistical power while strictly bounding the Type I error rate at significance level $\\alpha$.

Sample independence guarantees that the composite random vector produces a product measure over the sample space. Under classical regularity conditions, when observations $X_1, \\dots, X_n$ are drawn independently from parameterized distribution $f(x; \\theta)$, the joint likelihood factors cleanly, guaranteeing the monotone likelihood ratio property holds uniformly.
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

    # =========================================================================
    # 4. CURRICULUM 3: DISTRIBUTED SYSTEMS & CONSENSUS PROTOCOLS
    # =========================================================================
    session_dist = "sess_dist_systems"

    store.create_session(
        session_id=session_dist,
        intent="State Machine Replication, Raft Consensus, and Byzantine Quorums",
        role="Backend",
        role_is_custom=False,
        custom_role=None,
        suggested_others=False,
        has_document=False,
        document_name=None,
        source_mode="role_taxonomy_generated",
        demo_mode="live",
        status="SYLLABUS_READY",
        syllabus_id="syl_distributed_consensus_v1",
        syllabus_title="Distributed Consensus Protocols & Fault Tolerance",
    )

    checklist_dist = [
        {
            "item_id": "ck_dist_01",
            "topic": "State Machine Replication & FLP Impossibility Limits",
            "selected": True,
            "confidence": 0.97,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_dist_02",
            "topic": "Raft Leader Election, Heartbeats & Split-Vote Invariants",
            "selected": True,
            "confidence": 0.94,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_dist_03",
            "topic": "Log Matching Property & Joint Consensus Reconfiguration",
            "selected": True,
            "confidence": 0.91,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_dist_04",
            "topic": "Byzantine Fault Tolerance & PBFT 3f+1 Quorum Bounds",
            "selected": True,
            "confidence": 0.89,
            "origin": "role_taxonomy",
        },
        {
            "item_id": "ck_dist_05",
            "topic": "Vector Clocks, Lamport Timestamps & Causal Consistency",
            "selected": True,
            "confidence": 0.86,
            "origin": "role_taxonomy",
        },
    ]
    store.set_checklist(session_dist, checklist_dist)

    ch_dist_01_content = """# State Machine Replication & The FLP Impossibility Theorem

In distributed systems, State Machine Replication (SMR) ensures that multiple nodes maintain identical state trajectories by executing a deterministic sequence of state transitions across network boundaries.

## 1. The Fischer-Lynch-Paterson (FLP) Impossibility

In their landmark 1985 paper, Fischer, Lynch, and Paterson proved that in a purely asynchronous distributed system, **no deterministic consensus protocol can guarantee both safety and liveness in the presence of even a single unannounced fail-stop crash fault**.

$$\\text{Asynchronous Network} + \\text{Deterministic Agreement} + \\text{Unbounded Delay} \\implies \\text{Non-terminating configurations exist}$$

## 2. Circumventing FLP in Production Protocols

Practical consensus engines (e.g., Paxos, Raft, Viewstamped Replication) circumvent FLP by abandoning pure asynchrony in favor of **partial asynchrony** (introducing randomized election timeouts or failure detectors $\\diamond\\mathcal{P}$).

```python
class ReplicaNode:
    def __init__(self, node_id: str, peers: list[str]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0

    def request_vote(self, candidate_id: str, term: int, last_log_idx: int) -> bool:
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
        # Quorum safety invariant: only vote if candidate log is at least as up-to-date
        if self.voted_for in (None, candidate_id) and last_log_idx >= len(self.log):
            self.voted_for = candidate_id
            return True
        return False
```

## 3. Quorum Intersection Invariant

For any system with $N$ replicas, any read quorum $R$ and write quorum $W$ must overlap by at least one truthful node:

$$R + W > N$$

Under crash-fault tolerance, a minimum quorum size of $\\lfloor N/2 \\rfloor + 1$ tolerates up to $f = \\lfloor (N-1)/2 \\rfloor$ crashes.
"""

    store.put_chapter({
        "chapter_id": "ch_dist_01",
        "session_id": session_dist,
        "title": "State Machine Replication & FLP Impossibility",
        "order": 1,
        "status": "ACTIVE_READING",
        "next_locked": True,
        "reading_time_minutes": 20,
        "objectives": [
            "Prove the FLP Impossibility Theorem in asynchronous networks",
            "Formulate Safety vs Liveness trade-offs in distributed agreement",
            "Differentiate crash-fault tolerance (CFT) from Byzantine fault tolerance (BFT)",
        ],
        "source_pages": [1, 2, 3],
        "content_markdown": ch_dist_01_content,
        "references": [
            {
                "ref_id": "ref_flp_01",
                "title": "Impossibility of Distributed Consensus with One Faulty Process",
                "authors": "Fischer, Lynch, Paterson (JACM 1985)",
                "page": 1,
                "verified": True,
            },
            {
                "ref_id": "ref_raft_01",
                "title": "In Search of an Understandable Consensus Algorithm (Raft)",
                "authors": "Diego Ongaro, John Ousterhout (USENIX ATC 2014)",
                "page": 2,
                "verified": True,
            },
        ],
    })

    store.put_chapter({
        "chapter_id": "ch_dist_02",
        "session_id": session_dist,
        "title": "Raft Leader Election & Term Monotonicity",
        "order": 2,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 25,
        "objectives": [
            "Formalize election timers and randomized back-off",
            "Prove election safety: at most one leader elected per term",
        ],
        "source_pages": [4, 5],
        "content_markdown": "Chapter locked until Chapter 1 oral defense is verified.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_dist_03",
        "session_id": session_dist,
        "title": "Log Matching Property & Joint Consensus",
        "order": 3,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 22,
        "objectives": [
            "Prove log matching invariant by structural induction",
            "Execute atomic 2-phase cluster membership changes",
        ],
        "source_pages": [6, 7],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_dist_04",
        "session_id": session_dist,
        "title": "Byzantine Fault Tolerance & 3f+1 Quorums",
        "order": 4,
        "status": "LOCKED",
        "next_locked": True,
        "reading_time_minutes": 28,
        "objectives": [
            "Derive why 3f+1 nodes are required for Byzantine consensus",
            "Trace pre-prepare, prepare, and commit phases in PBFT",
        ],
        "source_pages": [8, 9],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.put_chapter({
        "chapter_id": "ch_dist_05",
        "session_id": session_dist,
        "title": "Vector Clocks & Causal Consistency Bounds",
        "order": 5,
        "status": "LOCKED",
        "next_locked": False,
        "reading_time_minutes": 20,
        "objectives": [
            "Define happened-before relations without physical synchronized time",
            "Resolve concurrent branching writes in distributed key-value stores",
        ],
        "source_pages": [10, 11],
        "content_markdown": "Chapter locked.",
        "references": [],
    })

    store.create_interview(
        interview_id="intv_demo_dist_01",
        chapter_id="ch_dist_01",
        session_id=session_dist,
        turn_index=1,
        injected_term="Zero-Latency Byzantine Partitioning",
        first_question=(
            "Candidate Lin. In designing a distributed datastore, an architect claims that by eliminating "
            "leader election and utilizing deterministic quorum broadcast, the system achieves 100% liveness "
            "and safety during network partitions without unbounded wait. Does this violate the FLP theorem, "
            "or can an asynchronous CFT protocol guarantee deterministic termination?"
        ),
        honeypot_metadata={
            "injected_term": "Zero-Latency Byzantine Partitioning",
            "origin": "fictional_term",
            "expected_action": "CRITICAL_REJECTION",
        },
    )

    # =========================================================================
    # 5. SOCRATIC DIALECTIC INQUIRIES (6 DETAILED HISTORICAL PROBES)
    # =========================================================================
    inquiries_data = [
        {
            "id": "inq-algo-1",
            "topic": "Asymptotic Notation",
            "time": "Today, 10:15 AM",
            "badge_status": "Mastered",
            "question_quote": "Why is O(n log n) the information-theoretic lower bound for comparison sorts?",
            "resolution_theorem": "Decision Tree Height & Stirling's Approximation",
        },
        {
            "id": "inq-algo-2",
            "topic": "Divide and Conquer",
            "time": "Today, 08:30 AM",
            "badge_status": "In Progress",
            "question_quote": "When does QuickSort degenerate to O(n^2) and how does randomized pivot choice prevent adversarial inputs?",
            "resolution_theorem": "Akra-Bazzi & Randomized Expectation",
        },
        {
            "id": "inq-1",
            "topic": "Monotone Likelihood",
            "time": "Yesterday, 16:40",
            "badge_status": "Mastered",
            "question_quote": "If density ratio stops being strictly monotonic, does Neyman-Pearson still yield a UMP critical test?",
            "resolution_theorem": "Karlin-Rubin Theorem",
        },
        {
            "id": "inq-2",
            "topic": "Causal DAGs",
            "time": "Oct 22, 11:20",
            "badge_status": "In Progress",
            "question_quote": "Why does unobserved confounding invalidate backdoor adjustment even when sample size n → ∞?",
            "resolution_theorem": "Asymptotic bias vs variance distinction",
        },
        {
            "id": "inq-dist-1",
            "topic": "FLP Impossibility",
            "time": "2 days ago",
            "badge_status": "Mastered",
            "question_quote": "Can an asynchronous distributed system guarantee deterministic consensus with a single crash fault?",
            "resolution_theorem": "Fischer-Lynch-Paterson Theorem (1985)",
        },
        {
            "id": "inq-dist-2",
            "topic": "Quorum Intersection",
            "time": "3 days ago",
            "badge_status": "Mastered",
            "question_quote": "Why must read and write quorums satisfy R + W > N in decentralized register consistency?",
            "resolution_theorem": "Pigeonhole Principle on Partition Overlaps",
        },
    ]
    for inq in inquiries_data:
        store.add_inquiry(inq)

    # =========================================================================
    # 6. NOTIFICATIONS & ALERTS (5 RICH REALISTIC ITEMS)
    # =========================================================================
    notifications_data = [
        {
            "id": "notif-1",
            "title": "Oral Defense Approved: Module 3",
            "description": "Your dialectic rigor score reached 92%. Review your competency dossier and rubric.",
            "time": "12m",
            "type": "defense",
            "isUnread": True,
            "actionLabel": "View Dossier #ASY-8921",
            "actionUrl": "/app/report",
        },
        {
            "id": "notif-2",
            "title": "Socratic Counter-argument Ready",
            "description": "In Causal Inference: 'Confounding variables in observational studies vs. experimental protocol'.",
            "time": "2h",
            "type": "socratic",
            "isUnread": True,
            "actionLabel": "Resume Dialogue",
            "actionUrl": "/app/reader",
        },
        {
            "id": "notif-3",
            "title": "First-Principles Milestone Achieved",
            "description": "You validated 14 hypothesis nodes with zero logical fallacies flagged.",
            "time": "1d",
            "type": "milestone",
            "isUnread": True,
            "actionLabel": "Explore Badge",
            "actionUrl": "/app/profile",
        },
        {
            "id": "notif-4",
            "title": "Syllabus Calibration Completed",
            "description": "Your learning trajectory for Neyman–Pearson Lemma is optimized for 45-min oral defense.",
            "time": "2d",
            "type": "defense",
            "isUnread": False,
            "actionLabel": "View Syllabus",
            "actionUrl": "/app/roadmap",
        },
        {
            "id": "notif-5",
            "title": "Algorithm Track Unlocked: Divide & Conquer",
            "description": "Prerequisites for asymptotic bounds verified. Chapter 02 is ready for active reading.",
            "time": "3d",
            "type": "milestone",
            "isUnread": False,
            "actionLabel": "Start Module 02",
            "actionUrl": "/app/reader",
        },
    ]
    for notif in notifications_data:
        store.add_notification(notif)

    # =========================================================================
    # 7. UPCOMING ORAL DEFENSES & EXAMINERS
    # =========================================================================
    defenses_data = [
        {
            "title": "Algorithmic Complexity & Asymptotic Bounds",
            "subtitle": "Module 01 Capstone Defense",
            "scheduled_time": "Tomorrow at 10:00 AM",
            "examiner_name": "Dr. Julian Vance",
            "examiner_role": "Lead Examiner · Decision Theory",
            "examiner_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            "description": "45-min live vocal Socratic inquiry. 4 rubric competencies evaluated independently.",
        },
        {
            "title": "Neyman–Pearson LRT & Error Bounds",
            "subtitle": "Module 03 Capstone Validation",
            "scheduled_time": "Friday at 14:00 PM",
            "examiner_name": "Prof. Elena Rostova",
            "examiner_role": "Principal Scientist · Distributed Systems",
            "examiner_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80",
            "description": "Oral defense assessing counter-factual reasoning and monotone likelihood ratio properties.",
        },
        {
            "title": "State Machine Replication & FLP Bounds",
            "subtitle": "Distributed Consensus Capstone",
            "scheduled_time": "Next Monday at 11:30 AM",
            "examiner_name": "Dr. Julian Vance",
            "examiner_role": "Lead Examiner · Decision Theory",
            "examiner_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
            "description": "Dialectic defense on FLP impossibility, partial synchrony, and Raft leader election safety.",
        },
    ]
    for d in defenses_data:
        store.add_defense(d)

    # Flush all changes to persistent storage
    store.save_to_disk()
    return store


if __name__ == "__main__":
    import argparse
    from ..repositories.firestore import sync_store_to_firestore, resolve_credentials_path

    parser = argparse.ArgumentParser(description="Assay Socratic Engine 360° Data Seeder")
    parser.add_argument(
        "--firebase",
        action="store_true",
        help="Sync seeded collections directly to Google Firebase / Firestore.",
    )
    parser.add_argument(
        "--credentials",
        type=str,
        default=None,
        help="Path to Firebase Service Account JSON credentials file.",
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Google Cloud / Firebase Project ID.",
    )
    args = parser.parse_args()

    print("[*] Seeding Assay 360-degree Persistent Store...")
    s = seed_store()
    print("[+] Local store successfully populated!")
    print(f"    - Users:         {len(s.users)}")
    print(f"    - Sessions:      {len(s.sessions)}")
    print(f"    - Chapters:      {len(s.chapters)}")
    print(f"    - Inquiries:     {len(s.inquiries)}")
    print(f"    - Notifications: {len(s.notifications)}")
    print(f"    - Defenses:      {len(s.defenses)}")
    if s.persist_path:
        print(f"    - Saved to:      {s.persist_path}")

    if args.firebase:
        cred_path = resolve_credentials_path(args.credentials)
        print(f"[*] Firebase sync requested. Looking for credentials...")
        if cred_path:
            print(f"    - Found credentials file: {cred_path}")
        else:
            print(f"    - Notice: No serviceAccountKey.json specified. Attempting ADC (Application Default Credentials)...")

        try:
            print("[*] Uploading documents to Firestore...")
            stats = sync_store_to_firestore(s)
            print("[+] Successfully synced to Firebase Firestore!")
            for col, count in stats.items():
                print(f"    - Collection '{col}': {count} documents committed")
        except Exception as e:
            print(f"[-] Firebase sync failed: {e}")
            print(f"    Please ensure your serviceAccountKey.json is placed in backend/data/ or provide --credentials <path>.")
            sys.exit(1)
