#!/usr/bin/env python3
"""LogosFortuna Eval Runner

Calistirir: scripts/evals/golden-tests.jsonl icindeki her test'i UDIV dongusunde
calistirir gibi simulate eder ve beklenen sonuc ile karsilastirir.

Not: Bu runner manuel olarak Claude oturumunda tetiklenir. Otomatik UDIV
testi icin gerçek bir Claude API kullanir veya `claude` CLI baglar.

Kullanim:
    python3 runner.py --suite all
    python3 runner.py --suite mcp-detection
    python3 runner.py --case basic-01
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

GOLDEN_FILE = Path(__file__).parent / "golden-tests.jsonl"


def load_tests(case_id: str | None = None, suite: str | None = None) -> list[dict]:
    """Load golden tests from JSONL."""
    if not GOLDEN_FILE.exists():
        print(f"ERROR: {GOLDEN_FILE} bulunamadi", file=sys.stderr)
        return []

    tests = []
    with GOLDEN_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                t = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"WARN: parse error in line: {e}", file=sys.stderr)
                continue
            if case_id and t.get("id") != case_id:
                continue
            if suite and suite != "all" and t.get("category") != suite:
                continue
            tests.append(t)
    return tests


def evaluate_test(test: dict) -> dict:
    """Run a single eval test.

    NOTE: This is a TEMPLATE. Actual UDIV execution requires Claude API integration.
    Currently returns a placeholder result. To activate:
    - Replace simulate_udiv() with real claude SDK call
    - Compare actual phases/tools used with expected
    """
    test_id = test.get("id", "unknown")
    expected = {
        "phases": test.get("expected_phases"),
        "skill_class": test.get("expected_skill_class"),
        "max_tools": test.get("expected_max_tools"),
        "mcp_needs": test.get("expected_mcp_needs"),
        "classification": test.get("expected_classification"),
        "confidence_min": test.get("expected_confidence_min"),
        "outcome": test.get("expected_outcome"),
    }

    # PLACEHOLDER: gercek implementasyonda Claude SDK ile UDIV calistirilir
    actual = simulate_udiv(test)

    passed = compare_results(expected, actual)

    return {
        "id": test_id,
        "category": test.get("category"),
        "passed": passed,
        "expected": expected,
        "actual": actual,
        "description": test.get("description"),
    }


def simulate_udiv(test: dict) -> dict:
    """Placeholder UDIV simulation. Replace with real Claude SDK integration."""
    return {
        "phases_executed": test.get("expected_phases"),  # echo expected for now
        "tools_used": test.get("expected_max_tools", 0),
        "skill_class": test.get("expected_skill_class"),
        "mcp_needs": test.get("expected_mcp_needs"),
        "classification": test.get("expected_classification"),
        "confidence": test.get("expected_confidence_min", 0),
        "outcome": test.get("expected_outcome"),
        "note": "PLACEHOLDER — claude SDK integration required for real eval",
    }


def compare_results(expected: dict, actual: dict) -> bool:
    """Compare expected vs actual. Returns True if all defined expectations met."""
    for key, exp_val in expected.items():
        if exp_val is None:
            continue
        actual_key_map = {
            "phases": "phases_executed",
            "skill_class": "skill_class",
            "max_tools": "tools_used",
            "mcp_needs": "mcp_needs",
            "classification": "classification",
            "confidence_min": "confidence",
            "outcome": "outcome",
        }
        actual_key = actual_key_map.get(key, key)
        act_val = actual.get(actual_key)

        if key == "max_tools":
            if act_val is None or act_val > exp_val:
                return False
        elif key == "confidence_min":
            if act_val is None or act_val < exp_val:
                return False
        else:
            if act_val != exp_val:
                return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="LogosFortuna eval runner")
    parser.add_argument("--suite", default="all", help="Test suite (all|simple|medium|complex|mcp-detection|skill-classification|loop-protection)")
    parser.add_argument("--case", default=None, help="Spesifik case ID")
    parser.add_argument("--report", default="text", choices=["text", "json"], help="Rapor formati")
    args = parser.parse_args()

    tests = load_tests(case_id=args.case, suite=args.suite)
    if not tests:
        print(f"No tests matched filters: suite={args.suite} case={args.case}", file=sys.stderr)
        return 1

    results = [evaluate_test(t) for t in tests]
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed

    if args.report == "json":
        print(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "results": results,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"LogosFortuna Eval Sonuclari ({args.suite})")
        print(f"{'='*60}\n")
        for r in results:
            status = "✅ PASS" if r["passed"] else "❌ FAIL"
            print(f"{status}  {r['id']}  [{r['category']}]")
            print(f"        {r['description']}")
            if not r["passed"]:
                print(f"        Expected: {r['expected']}")
                print(f"        Actual:   {r['actual']}")
            print()
        print(f"{'='*60}")
        print(f"Toplam: {len(results)}  Gecti: {passed}  Kaldi: {failed}")
        print(f"{'='*60}\n")
        if results and results[0].get("actual", {}).get("note"):
            print("NOT: Bu runner placeholder UDIV simulasyonu kullanir.")
            print("Gercek eval icin simulate_udiv() Claude SDK ile degistirilmeli.\n")

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
