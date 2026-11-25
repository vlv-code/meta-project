#!/usr/bin/env python3
"""High-performance parallel test runner for Meta-Project test suite.

Features:
- Zero external dependencies: Python 3.10+ standard library only.
- Process-level isolation using concurrent.futures.ProcessPoolExecutor.
- LPT (Longest Processing Time) class scheduling: executes heavier classes first.
- Real-time progress indicators, timing summaries, and failure isolation.
- Exit code parity: 0 for all passed/skipped, 1 on any failure or error.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib
import io
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
TESTS_DIR = REPO_ROOT / "tests"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


def _run_test_case_class(
    test_module_name: str,
    test_class_name: str,
    failfast: bool = False,
) -> Dict[str, Any]:
    """Worker task: execute all tests in a single TestCase class."""
    start_time = time.perf_counter()
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        sys.stdout = stdout_buf
        sys.stderr = stderr_buf

        mod = importlib.import_module(test_module_name)
        cls = getattr(mod, test_class_name)
        suite = unittest.TestLoader().loadTestsFromTestCase(cls)

        result = unittest.TestResult()
        result.failfast = failfast
        suite.run(result)

        elapsed = time.perf_counter() - start_time

        failures = [(str(t), err) for t, err in result.failures]
        errors = [(str(t), err) for t, err in result.errors]
        skipped = [(str(t), reason) for t, reason in result.skipped]

        return {
            "module": test_module_name,
            "class": test_class_name,
            "tests_run": result.testsRun,
            "failures": failures,
            "errors": errors,
            "skipped": skipped,
            "elapsed": elapsed,
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "success": result.wasSuccessful(),
        }
    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        import traceback

        tb = traceback.format_exc()
        return {
            "module": test_module_name,
            "class": test_class_name,
            "tests_run": 0,
            "failures": [],
            "errors": [(f"{test_module_name}.{test_class_name}", f"{exc}\n{tb}")],
            "skipped": [],
            "elapsed": elapsed,
            "stdout": stdout_buf.getvalue(),
            "stderr": stderr_buf.getvalue(),
            "success": False,
        }
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def discover_test_classes(
    tests_dir: Path, pattern: str = "test_*.py"
) -> List[Tuple[str, str, int]]:
    """Discover all TestCase classes and sort by estimated execution weight (LPT)."""
    loader = unittest.TestLoader()
    suite = loader.discover(str(tests_dir), pattern=pattern)

    classes_map: Dict[Tuple[str, str], int] = {}

    def _extract_tests(item: Any) -> None:
        if isinstance(item, unittest.TestCase):
            key = (item.__class__.__module__, item.__class__.__name__)
            classes_map[key] = classes_map.get(key, 0) + 1
        elif isinstance(item, unittest.TestSuite):
            for sub in item:
                _extract_tests(sub)

    _extract_tests(suite)

    def _weight(entry: Tuple[Tuple[str, str], int]) -> int:
        (mod, cls), count = entry
        score = count
        lower_name = f"{mod}.{cls}".lower()
        if "update" in lower_name:
            score += 200
        elif "manage" in lower_name:
            score += 80
        elif "acceptance" in lower_name:
            score += 50
        elif "boundaries" in lower_name:
            score += 30
        return score

    sorted_classes = sorted(classes_map.items(), key=_weight, reverse=True)
    return [(mod, cls, count) for (mod, cls), count in sorted_classes]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parallel stdlib test runner for Meta-Project"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=min(8, os.cpu_count() or 4),
        help="Number of parallel worker processes (default: min(8, cpu_count))",
    )
    parser.add_argument(
        "--pattern",
        "-p",
        default="test_*.py",
        help="Pattern to match test files (default: test_*.py)",
    )
    parser.add_argument(
        "--failfast",
        "-f",
        action="store_true",
        help="Stop on first failure or error",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args(argv)

    print(
        f"==> Discovering test suites in '{TESTS_DIR}' (pattern: '{args.pattern}')..."
    )
    class_items = discover_test_classes(TESTS_DIR, pattern=args.pattern)

    total_classes = len(class_items)
    estimated_tests = sum(c[2] for c in class_items)
    print(
        f"==> Scheduled {estimated_tests} tests across {total_classes} TestCase classes on {args.workers} worker(s) (LPT priority queue)."
    )

    start_wall = time.perf_counter()

    results: List[Dict[str, Any]] = []
    total_run = 0
    total_failures: List[Tuple[str, str, str]] = []
    total_errors: List[Tuple[str, str, str]] = []
    total_skipped: List[Tuple[str, str, str]] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_cls = {
            executor.submit(
                _run_test_case_class, mod, cls, args.failfast
            ): (mod, cls)
            for mod, cls, _ in class_items
        }

        for future in concurrent.futures.as_completed(future_to_cls):
            mod, cls = future_to_cls[future]
            try:
                res = future.result()
            except Exception as e:
                import traceback

                res = {
                    "module": mod,
                    "class": cls,
                    "tests_run": 0,
                    "failures": [],
                    "errors": [(f"{mod}.{cls}", f"Executor exception: {e}\n{traceback.format_exc()}")],
                    "skipped": [],
                    "elapsed": 0.0,
                    "stdout": "",
                    "stderr": "",
                    "success": False,
                }

            results.append(res)
            total_run += res["tests_run"]

            for tname, trace in res["failures"]:
                total_failures.append((res["module"], tname, trace))
            for tname, trace in res["errors"]:
                total_errors.append((res["module"], tname, trace))
            for tname, reason in res["skipped"]:
                total_skipped.append((res["module"], tname, reason))

            if args.verbose:
                status = "PASS" if res["success"] else "FAIL"
                print(
                    f"[{status}] {res['module']}.{res['class']} ({res['tests_run']} tests, {res['elapsed']:.2f}s)"
                )
            else:
                if not res["success"]:
                    sys.stdout.write("F" if res["failures"] else "E")
                elif res["skipped"]:
                    sys.stdout.write("s")
                else:
                    sys.stdout.write(".")
                sys.stdout.flush()

            if args.failfast and not res["success"]:
                print("\n[FAILFAST] Aborting remaining jobs due to failure.")
                executor.shutdown(wait=False, cancel_futures=True)
                break

    if not args.verbose:
        sys.stdout.write("\n")
        sys.stdout.flush()

    total_wall = time.perf_counter() - start_wall

    # Print failures and errors
    if total_failures or total_errors:
        print("\n" + "=" * 70)
        print("FAILURES AND ERRORS:")
        print("=" * 70)
        for mod, tname, trace in total_failures:
            print(f"\nFAIL: {tname} ({mod})")
            print("-" * 70)
            print(trace)
        for mod, tname, trace in total_errors:
            print(f"\nERROR: {tname} ({mod})")
            print("-" * 70)
            print(trace)

    print("\n" + "=" * 70)
    print("TEST EXECUTION SUMMARY:")
    print("=" * 70)
    print(f"Total Tests Run   : {total_run}")
    print(f"Classes Executed  : {len(results)} / {total_classes}")
    print(f"Failures          : {len(total_failures)}")
    print(f"Errors            : {len(total_errors)}")
    print(f"Skipped           : {len(total_skipped)}")
    print(f"Wall-Clock Time   : {total_wall:.2f}s")
    if class_items:
        cumulative_time = sum(r["elapsed"] for r in results)
        speedup = cumulative_time / max(0.001, total_wall)
        print(f"Cumulative CPU Time: {cumulative_time:.2f}s ({speedup:.1f}x parallel speedup)")

    # Print top 5 slowest classes
    slowest = sorted(results, key=lambda r: r["elapsed"], reverse=True)[:5]
    print("\nTop 5 Slowest TestCase Classes:")
    for i, s in enumerate(slowest, 1):
        print(f"  {i}. {s['module']}.{s['class']} ({s['tests_run']} tests) - {s['elapsed']:.2f}s")
    print("=" * 70)

    is_success = len(total_failures) == 0 and len(total_errors) == 0
    if is_success:
        print("[OK] All tests passed.")
        return 0
    else:
        print("[FAIL] Test battery finished with errors.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
