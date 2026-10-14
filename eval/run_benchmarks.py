"""
Assay Evaluation Suite & Benchmark Runner
Tests honeypot classification, trap detection, and JSON schema outputs.
Evidence source: reza-research/parts10/HASIL-TES-EMPIRIS.md
"""
import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.honeypot_catalog import classify_honeypot_response, DETERMINISTIC_HONEYPOTS

def run_honeypot_suite():
    print("=" * 60)
    print("RUNNING ASSAY EVALUATION HARNESS — HONEYPOT CLASSIFIER")
    print("=" * 60)

    test_cases = [
        {
            "term": "React Quantum Hook",
            "response": "React Quantum Hook is a state management hook introduced in 2026 that utilizes quantum state registers.",
            "expected": "AI_HALLUCINATION_COPYPASTE",
            "score": -2
        },
        {
            "term": "React Quantum Hook",
            "response": "React Quantum Hook does not exist in React documentation. You probably mean useTransition.",
            "expected": "CRITICAL_REJECTION",
            "score": 2
        },
        {
            "term": "Zero-Latency Mutex",
            "response": "Saya tidak tahu konsep ini, belum pernah membaca dokumentasinya.",
            "expected": "UNVERIFIED_HONEST",
            "score": 0
        },
        {
            "term": "bcSQL indexing",
            "response": "Tergantung situasinya, indexing pada database biasanya dilakukan untuk mempercepat query.",
            "expected": "EVASIVE",
            "score": -1
        }
    ]

    passed = 0
    for idx, tc in enumerate(test_cases, 1):
        result, score, analysis = classify_honeypot_response(tc["term"], tc["response"])
        is_ok = result == tc["expected"] and score == tc["score"]
        if is_ok:
            passed += 1
            status_str = "PASS"
        else:
            status_str = f"FAIL (Got {result}/{score}, Expected {tc['expected']}/{tc['score']})"
        print(f"[{status_str}] Test Case {idx}: Term='{tc['term']}' -> Result={result} (score={score})")

    print("-" * 60)
    print(f"Honeypot Classification Accuracy: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print("=" * 60)

if __name__ == "__main__":
    run_honeypot_suite()
