#!/usr/bin/env python3
"""
Wave D, dispatcher integration tail — D6 continuation: cross-pin merge base.

Live acceptance scenario S1 (auditor iteration recommendation: "two sequential
updates with adaptations") exposed a plan gap after Lanes E1/E2: the same-pin
base was fixed (pinned bundle seeds base candidates), but a v1 -> v2 update on
a consumer WITHOUT a populated cache still refused with needs_base — although
the lock-recorded base revision is fully available in the origin repository's
git history. The engine must fetch merge-base candidates from the origin at
the lock's recorded source commit (hash-verified), not only from cache dirs.

RED contract: test_cross_pin_merge_base_fetched_from_origin_history fails on
the post-E2 engine (needs_base refusal), then goes GREEN.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_update_meta_project import (  # fixture reuse (same package)
    ACTOR_ID,
    INSTALLATION_ID,
    ORIGIN_X_V1,
    ORIGIN_X_V2,
    _git_ok,
    _make_origin_repo,
)

from scripts.update_meta_project import (
    apply_updates,
    load_bundle,
    plan_updates,
    read_lock,
    resolve_source,
)

CODE_MARKER_OPEN = b"# local_repo_data:hotfix"
CODE_MARKER_CLOSE = b"# /local_repo_data:hotfix"
CODE_MARKER_BODY = b"HOTFIX: cross-pin base must come from origin history."


def _git_init(path: Path) -> None:
    _git_ok(path, "init", "-q", "-b", "main")
    _git_ok(path, "commit", "-q", "--allow-empty", "-m", "baseline")


class TestCrossPinOriginBaseFetch(unittest.TestCase):
    def test_cross_pin_merge_base_fetched_from_origin_history(self):
        """v1 install (empty cache) -> marked local edit -> v2 update must
        MERGE (marker preserved), not refuse with needs_base."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            origin, sha1 = _make_origin_repo(tmp)
            sha2 = _git_ok(origin, "rev-parse", "HEAD").stdout.strip()

            empty_cache = tmp / "empty-cache"
            empty_cache.mkdir()
            target = tmp / "consumer"
            target.mkdir()
            _git_init(target)

            # --- first install: engine creates files + lock (pin = sha1) ---
            pin1 = resolve_source(str(origin), sha1)
            bundle1 = load_bundle(pin1, empty_cache)
            plan1 = plan_updates(target, bundle1, None)
            self.assertEqual(plan1["conflicts"], [])
            self.assertEqual(plan1["needs_base"], [])
            result1 = apply_updates(
                target, plan1, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin1
            )
            self.assertEqual(result1["status"], "completed")
            installed = (target / "scripts" / "x.py").read_bytes()
            self.assertEqual(installed, ORIGIN_X_V1)
            lock1 = read_lock(target)
            self.assertEqual(
                lock1["source"]["commit_sha"], sha1, "lock must pin sha1"
            )

            # --- marked local adaptation (code-form marker, D7) ---
            x_path = target / "scripts" / "x.py"
            x_path.write_bytes(
                ORIGIN_X_V1
                + CODE_MARKER_OPEN
                + b"\n"
                + CODE_MARKER_BODY
                + b"\n"
                + CODE_MARKER_CLOSE
                + b"\n"
            )

            # --- second update: v1 -> v2, STILL an empty cache ---
            pin2 = resolve_source(str(origin), sha2)
            bundle2 = load_bundle(pin2, empty_cache)
            plan2 = plan_updates(target, bundle2, read_lock(target))

            needs = [e["path"] for e in plan2["needs_base"]]
            self.assertEqual(
                needs,
                [],
                f"cross-pin base must be fetched from origin history, got needs_base: {needs}",
            )
            merges = {
                a["path"]: a for a in plan2["actions"] if a.get("op") == "merge"
            }
            self.assertIn("scripts/x.py", merges, "x.py must be a merge action")

            result2 = apply_updates(
                target, plan2, ACTOR_ID, INSTALLATION_ID, resolved_pin=pin2
            )
            self.assertEqual(result2["status"], "completed")
            final = x_path.read_bytes()
            self.assertIn(ORIGIN_X_V2, final, "upstream v2 content applied")
            self.assertIn(
                CODE_MARKER_BODY, final, "marked adaptation preserved (auditor п.1/S1)"
            )


if __name__ == "__main__":
    unittest.main()
