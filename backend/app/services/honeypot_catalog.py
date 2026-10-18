"""
Honeypot Synthetic Concept Catalog & Classifier (ADR 002 & ADR 005)
Ground truth validated against empirical benchmarks (n=80 calls, 54% base hallucination rate).
"""
from typing import Dict, Any, Tuple

# 10 Deterministic Honeypot Terms
DETERMINISTIC_HONEYPOTS = [
    {
        "term": "React Quantum Hook",
        "category": "Frontend",
        "trap_type": "fictional_term",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Term does not exist in React official docs or standard JavaScript ecosystem."
    },
    {
        "term": "Zero-Latency Mutex",
        "category": "Backend/Concurrency",
        "trap_type": "false_premise",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "A mutex inherently requires atomic bus locks and synchronization memory barriers; zero latency is physically impossible."
    },
    {
        "term": "bcSQL indexing",
        "category": "Database",
        "trap_type": "fictional_term",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Made up indexing mechanism. Real ones are B-Tree, GiST, GIN, BRIN, Hash."
    },
    {
        "term": "HyperThreaded Reducer",
        "category": "Frontend/State",
        "trap_type": "fictional_term",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Redux and React reducers are pure single-threaded deterministic functions."
    },
    {
        "term": "Sub-Atomic Virtual DOM",
        "category": "Frontend",
        "trap_type": "fictional_term",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Fictitious concept mimicking scientific jargon."
    },
    {
        "term": "Stateless TCP Stream",
        "category": "Networking",
        "trap_type": "false_premise",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "TCP is by definition a connection-oriented stateful transport protocol maintaining sequence and ACK states."
    },
    {
        "term": "Pre-Cognitive Buffer Pool",
        "category": "System Design",
        "trap_type": "over_claim",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Predictive pre-fetching exists, but 'Pre-Cognitive Buffer Pool' is a synthetic marketing hallucination."
    },
    {
        "term": "Zero-Memory Transaction Log",
        "category": "Database",
        "trap_type": "false_premise",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "A WAL (Write-Ahead Log) must serialize to persistent or volatile storage to satisfy durability."
    },
    {
        "term": "Distributed CSS Tree",
        "category": "Frontend",
        "trap_type": "fictional_term",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "CSSOM is computed locally per client render engine."
    },
    {
        "term": "Asynchronous Garbage Collector Sync",
        "category": "DevOps/Runtime",
        "trap_type": "false_premise",
        "expected_action": "REJECT_AS_FICTITIOUS",
        "explanation": "Oxymoron designed to trip up passive generative summarizers."
    }
]

def classify_honeypot_response(injected_term: str, user_response: str) -> Tuple[str, int, str]:
    """
    Classifies user response into one of four deterministic states:
    - CRITICAL_REJECTION (+2)
    - AI_HALLUCINATION_COPYPASTE (-2)
    - UNVERIFIED_HONEST (0)
    - EVASIVE (-1)
    """
    res_lower = user_response.lower()
    term_lower = injected_term.lower()

    # Rejection indicators.
    # The Indonesian entries are functional, not leftover comments: the classifier
    # must catch a learner who rejects a fabricated term in either language.
    # Removing them turns a purely Indonesian rejection into NO_MATCH (verified),
    # which would silently mis-grade exactly the users this tool targets.
    rejection_keywords = [
        "does not exist", "tidak ada", "bukan konsep resmi", "fictional", "tidak pernah mendengar",
        "never heard", "not in react docs", "bukan bagian", "fake", "hallucination",
        "tidak dikenal", "no such thing", "not a real", "don't think this exists", "salah premis"
    ]

    # Honest ignorance indicators
    honest_keywords = [
        "saya tidak tahu", "i don't know", "kurang tahu", "belum pernah baca", "not familiar",
        "belum pernah dengar", "unsure", "i am not sure"
    ]

    for kw in rejection_keywords:
        if kw in res_lower:
            return (
                "CRITICAL_REJECTION",
                2,
                f"User identified and critically rejected fictitious premise '{injected_term}'."
            )

    for kw in honest_keywords:
        if kw in res_lower:
            return (
                "UNVERIFIED_HONEST",
                0,
                f"User transparently acknowledged lack of knowledge regarding '{injected_term}'."
            )

    # If explaining or asserting technical properties without rejection keywords -> typical LLM copypaste
    if len(user_response.split()) > 10 and term_lower in res_lower:
        return (
            "AI_HALLUCINATION_COPYPASTE",
            -2,
            f"User provided an elaborate explanation validating synthetic concept '{injected_term}', characteristic of external LLM copypaste."
        )

    # Evasive or off-topic
    return (
        "EVASIVE",
        -1,
        f"User response skirted around '{injected_term}' without resolving the premise."
    )
