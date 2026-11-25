#!/usr/bin/env python3
"""Canonical domain test suite for triage_incident (scripts/triage_incident.py).

Consolidated in Wave T (Lane T2) from tests/test_kwave_t.py.
Zero-dependency: Python 3.10+ stdlib only.
"""


from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "templates" / "release_manifest.json"
SCRIPT_PATH = REPO_ROOT / "scripts" / "triage_incident.py"
SKILL_PATH = REPO_ROOT / "skills" / "triage-incident" / "SKILL.md"
MIRROR_SKILL_PATH = REPO_ROOT / ".agents" / "skills" / "triage-incident" / "SKILL.md"

ACTOR = "acme/app::antigravity::ag-main::agent-dev-lead"
TARGET_ROLE = "agent-devops-infra"


def _run_triage(args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class TempWorkspaceTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="triage_incident_")
        self.root = Path(self.temp_dir).resolve()
        self.tasks_path = self.root / "tasks.md"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_tasks(self, content: str) -> Path:
        self.tasks_path.write_text(content, encoding="utf-8")
        return self.tasks_path


class TestTriageProbeAndCircuitBreaker(TempWorkspaceTestCase):
    """probe creates - [?] PROBE and trips diagnostic Circuit Breaker on rev >= 2 without evidence."""

    def test_first_probe_creates_probe_record_and_preserves_foreign_entries(self):
        foreign = (
            "# Current and Active Project Tasks\n\n"
            "## Execution Plan and Checklist\n"
            "- [x] [acme/app::antigravity::ag-main::agent-other @ 2026-11-24 09:00] Keep me verbatim\n"
            "- [ ] [acme/app::antigravity::ag-main::agent-other @ 2026-11-24 09:10] Foreign pending task\n\n"
            "---\n\n"
            "## Delegated Subtasks and Blockers\n"
            "- `[agent-other -> agent-qa @ 2026-11-24 09:15]`: Existing blocker.\n"
        )
        self._seed_tasks(foreign)

        res = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-101",
            "--symptom", "Output zip contains template defaults instead of build config",
            "--hypothesis", "Cached stub overwritten before build",
            "--discriminator", "Compare artifact sha256 against template file",
        ])
        self.assertEqual(res.returncode, 0, f"probe failed: {res.stderr}\n{res.stdout}")
        text = self.tasks_path.read_text(encoding="utf-8")
        self.assertIn(f"- [?] PROBE [{ACTOR} @ ", text)
        self.assertIn("INC-101", text)
        self.assertIn("revisions: 1", text)
        self.assertIn("Cached stub overwritten before build", text)
        self.assertIn("- [x] [acme/app::antigravity::ag-main::agent-other @ 2026-11-24 09:00] Keep me verbatim", text)
        self.assertIn("- `[agent-other -> agent-qa @ 2026-11-24 09:15]`: Existing blocker.", text)

    def test_second_probe_without_new_evidence_triggers_circuit_breaker(self):
        res1 = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-102",
            "--symptom", "Silent failure on packaging",
            "--hypothesis", "H1: wrong flag passed",
            "--discriminator", "Inspect CLI argv",
        ])
        self.assertEqual(res1.returncode, 0, res1.stderr)
        before_second = self.tasks_path.read_text(encoding="utf-8")

        res2 = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-102",
            "--symptom", "Silent failure on packaging",
            "--hypothesis", "H2: stale env var in container",
            "--discriminator", "Echo container env",
        ])
        self.assertEqual(res2.returncode, 1, "2nd revision without evidence must fail closed")
        self.assertIn("[TRIAGE_CIRCUIT_BREAKER]", res2.stderr)
        self.assertIn("expected:", res2.stderr.splitlines()[0])
        self.assertIn("actual:", res2.stderr.splitlines()[0])
        self.assertIn("next:", res2.stderr.splitlines()[0])
        # Fail-closed zero-write on refusal: H2 must not overwrite tasks.md
        self.assertEqual(self.tasks_path.read_text(encoding="utf-8"), before_second)

    def test_probe_succeeds_after_record_evidence_breaks_unverified_streak(self):
        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-103",
            "--symptom", "Installer lacks config",
            "--hypothesis", "H1: wrong input dir",
            "--discriminator", "Check file sha256",
        ]).returncode, 0)

        ev = _run_triage([
            "record-evidence",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-103",
            "--command", "python check_hash.py",
            "--observed", "Input dir correct, output IDENTICAL_BYTES to template",
        ])
        self.assertEqual(ev.returncode, 0, ev.stderr)

        # Now revising to H2 is permitted because new evidence was recorded after H1
        res2 = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-103",
            "--symptom", "Installer lacks config",
            "--hypothesis", "H2: packager CLI rejected manifest and fell back to template",
            "--discriminator", "Run packager with unmasked stderr",
        ])
        self.assertEqual(res2.returncode, 0, f"probe after new evidence must succeed: {res2.stderr}")
        text = self.tasks_path.read_text(encoding="utf-8")
        self.assertIn("revisions: 2", text)
        self.assertIn("H2: packager CLI rejected manifest", text)

        # A 3rd revision without new evidence after H2 MUST trip Circuit Breaker again
        res3 = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-103",
            "--symptom", "Installer lacks config",
            "--hypothesis", "H3: speculative guess without running stderr probe",
            "--discriminator", "Guess again",
        ])
        self.assertEqual(res3.returncode, 1)
        self.assertIn("[TRIAGE_CIRCUIT_BREAKER]", res3.stderr)


class TestRecordEvidenceAndPromoteGate(TempWorkspaceTestCase):
    """record-evidence computes artifact metadata; promote fails closed without evidence."""

    def test_promote_refuses_without_evidence_fail_closed(self):
        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "DIAG-1",
            "--symptom", "Setup binary uses defaults",
            "--hypothesis", "Packager silently fell back",
            "--discriminator", "Capture stderr",
        ]).returncode, 0)
        before_promote = self.tasks_path.read_text(encoding="utf-8")

        res = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "DIAG-1",
            "--root-cause", "Guessing root cause",
            "--fix-scope", "builder.py",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(res.returncode, 1, "promote without evidence must fail closed")
        self.assertIn("[EVIDENCE_REQUIRED]", res.stderr)
        # Must keep - [?] PROBE unchanged
        self.assertEqual(self.tasks_path.read_text(encoding="utf-8"), before_promote)

    def test_record_evidence_with_artifact_and_promote_succeeds(self):
        artifact = self.root / "dist_installer.bin"
        payload = b"REAL-PAYLOAD-12345"
        artifact.write_bytes(payload)
        expected_sha = hashlib.sha256(payload).hexdigest()

        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-200",
            "--symptom", "Stale installer emitted",
            "--hypothesis", "Absolute path rejected by packager",
            "--discriminator", "Run packager CLI directly in container",
        ]).returncode, 0)

        ev = _run_triage([
            "record-evidence",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-200",
            "--command", "container-exec packager --manifest m.json",
            "--observed", "exit=2 stderr='ERROR: absolute path forbidden in manifest'",
            "--artifact", str(artifact),
        ])
        self.assertEqual(ev.returncode, 0, ev.stderr)
        tasks_after_ev = self.tasks_path.read_text(encoding="utf-8")
        self.assertIn("evidence [", tasks_after_ev)
        self.assertIn(f"sha256={expected_sha}", tasks_after_ev)
        self.assertIn(f"size_bytes={len(payload)}", tasks_after_ev)
        self.assertIn("mtime_utc=", tasks_after_ev)

        prom = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-200",
            "--root-cause", "builder emits absolute paths rejected by container packager; catch-all swallowed stderr",
            "--fix-scope", "scripts/build_pkg.py",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(prom.returncode, 0, prom.stderr)
        tasks_after_prom = self.tasks_path.read_text(encoding="utf-8")
        self.assertNotIn("- [?] PROBE", tasks_after_prom)
        self.assertIn(f"- [ ] FIX [{ACTOR} @ ", tasks_after_prom)
        self.assertIn("INC-200", tasks_after_prom)
        self.assertIn(f"target_role: {TARGET_ROLE}", tasks_after_prom)
        # Verify Handoff Packet printed to stdout
        self.assertIn(f"### Task Handoff Package: [{ACTOR} -> {TARGET_ROLE}]", prom.stdout)
        self.assertIn("- Original goal:", prom.stdout)
        self.assertIn("- Completed work:", prom.stdout)
        self.assertIn("- Handoff boundary:", prom.stdout)
        self.assertIn(f"- Recommended prompt for {TARGET_ROLE}:", prom.stdout)

        # Second promote on already-promoted entry must fail cleanly (no duplicate fix state)
        prom2 = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-200",
            "--root-cause", "duplicate",
            "--fix-scope", "scripts/build_pkg.py",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(prom2.returncode, 1)

    def test_promote_rejects_unverified_trailing_hypothesis_and_passes_after_evidence(self):
        # probe(H1) -> record-evidence (E1) -> probe(H2) -> promote MUST fail (H2 unverified)
        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--symptom", "Setup falls back to defaults",
            "--hypothesis", "H1: wrong input directory",
            "--discriminator", "Check input directory contents",
        ]).returncode, 0)

        self.assertEqual(_run_triage([
            "record-evidence",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--command", "ls -la build_in",
            "--observed", "exit=0 build_in has valid manifest.json",
        ]).returncode, 0)

        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--symptom", "Setup falls back to defaults",
            "--hypothesis", "H2: packager rejected manifest silently",
            "--discriminator", "Run packager CLI without stderr redirect",
        ]).returncode, 0)

        before_promote = self.tasks_path.read_text(encoding="utf-8")
        prom_fail = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--root-cause", "packager rejected manifest",
            "--fix-scope", "scripts/pkg.py",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(
            prom_fail.returncode,
            1,
            f"promote with trailing unverified H2 must fail closed! stdout={prom_fail.stdout!r}",
        )
        self.assertIn("[EVIDENCE_REQUIRED]", prom_fail.stderr)
        self.assertEqual(self.tasks_path.read_text(encoding="utf-8"), before_promote)

        # After recording evidence for H2, promote MUST succeed and pass strict check-tasks
        self.assertEqual(_run_triage([
            "record-evidence",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--command", "packager --check manifest.json",
            "--observed", "exit=2 error='schema field rejected'",
        ]).returncode, 0)

        prom_ok = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-201",
            "--root-cause", "schema field rejected by packager",
            "--fix-scope", "scripts/pkg.py",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(prom_ok.returncode, 0, prom_ok.stderr)

        chk = _run_triage([
            "check-tasks",
            "--tasks", str(self.tasks_path),
            "--json",
            "--strict",
        ])
        self.assertEqual(chk.returncode, 0, chk.stderr)
        data = json.loads(chk.stdout)
        self.assertEqual(data["summary"]["unverified_count"], 0)
        self.assertEqual(data["summary"]["verified_count"], 1)
        self.assertEqual([item["id"] for item in data["verified_facts"]], ["INC-201"])


class TestCheckTasksClassifier(TempWorkspaceTestCase):
    """check-tasks classifies verified_facts, unverified_hypotheses, and thrashing_ids."""

    def test_check_tasks_detects_unverified_final_and_thrashing(self):
        sample = (
            "# Current and Active Project Tasks\n\n"
            "## Execution Plan and Checklist\n"
            "- [x] [actor-a @ 2026-11-24 08:00] Regular non-diagnostic refactor step\n"
            "- [x] [actor-a @ 2026-11-24 08:10] INC-10: финал — проблема точно в кэше\n"
            "- [?] PROBE [actor-b @ 2026-11-24 08:20] DIAG-2: root cause in parser\n"
            "  - hypothesis [1]: H1\n"
            "  - revisions: 2\n"
            "  - hypothesis [2]: H2\n"
            "- [ ] FIX [actor-c @ 2026-11-24 08:30] INC-11: verified missing quote\n"
            "  - evidence [actor-c @ 2026-11-24 08:29]: cmd=`cli --check` | observed=`SyntaxError line 4`\n"
            "- [ ] [actor-d @ 2026-11-24 08:40] proven broken env var PATH\n"
        )
        self._seed_tasks(sample)

        res = _run_triage([
            "check-tasks",
            "--tasks", str(self.tasks_path),
            "--json",
        ])
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)

        verified_ids = {item["id"] for item in data["verified_facts"]}
        unverified_ids = {item["id"] for item in data["unverified_hypotheses"]}
        thrashing_ids = set(data["thrashing_ids"])

        self.assertEqual(verified_ids, {"INC-11"})
        self.assertIn("INC-10", unverified_ids)
        self.assertIn("DIAG-2", unverified_ids)
        # The free-form "proven broken env var PATH" line has no explicit ID -> still caught
        self.assertGreaterEqual(len(data["unverified_hypotheses"]), 3)
        self.assertIn("DIAG-2", thrashing_ids)

        # --strict must fail closed (rc=1) when unverified or thrashing entries exist
        strict_res = _run_triage([
            "check-tasks",
            "--tasks", str(self.tasks_path),
            "--json",
            "--strict",
        ])
        self.assertEqual(strict_res.returncode, 1)
        self.assertIn("[UNVERIFIED_HYPOTHESES]", strict_res.stderr)

    def test_check_tasks_empty_or_nonstandard_tasks_file_is_clean(self):
        self._seed_tasks("")
        res = _run_triage([
            "check-tasks",
            "--tasks", str(self.tasks_path),
            "--json",
            "--strict",
        ])
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["verified_facts"], [])
        self.assertEqual(data["unverified_hypotheses"], [])
        self.assertEqual(data["thrashing_ids"], [])

    def test_check_tasks_ignores_fenced_examples_and_backticked_docs(self):
        sample = (
            "# Tasks\n\n"
            "## Rules\n"
            "6. Use `- [?] PROBE` then `evidence:` then `- [ ] FIX`.\n"
            "```markdown\n"
            "- [?] PROBE [actor @ 2026-11-24 00:00] DIAG-EXAMPLE: root cause sample\n"
            "```\n"
            "- [x] [actor @ 2026-11-24 09:00] Implemented `probe` and `check-tasks` CLI documentation\n"
        )
        self._seed_tasks(sample)
        res = _run_triage([
            "check-tasks",
            "--tasks", str(self.tasks_path),
            "--json",
            "--strict",
        ])
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertEqual(data["unverified_hypotheses"], [])
        self.assertEqual(data["thrashing_ids"], [])


class TestArtifactInspection(TempWorkspaceTestCase):
    """artifact inspects metadata and distinguishes IDENTICAL_BYTES vs DIFFERS."""

    def test_artifact_metadata_and_compare(self):
        a1 = self.root / "output.bin"
        a2_same = self.root / "template.bin"
        a3_diff = self.root / "real_build.bin"
        content = b"stub-template-bytes-v0"
        a1.write_bytes(content)
        a2_same.write_bytes(content)
        a3_diff.write_bytes(b"diff-content-bytes-v1")

        res_same = _run_triage([
            "artifact",
            "--path", str(a1),
            "--compare", str(a2_same),
            "--json",
        ])
        self.assertEqual(res_same.returncode, 0, res_same.stderr)
        d_same = json.loads(res_same.stdout)
        self.assertEqual(d_same["size_bytes"], len(content))
        self.assertEqual(d_same["sha256"], hashlib.sha256(content).hexdigest())
        self.assertRegex(d_same["mtime_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(d_same["comparison"], "IDENTICAL_BYTES")

        res_diff = _run_triage([
            "artifact",
            "--path", str(a1),
            "--compare", str(a3_diff),
            "--json",
        ])
        self.assertEqual(res_diff.returncode, 0, res_diff.stderr)
        d_diff = json.loads(res_diff.stdout)
        self.assertEqual(d_diff["comparison"], "DIFFERS")


class TestAdversarialHardening(TempWorkspaceTestCase):
    """Adversarial inputs: traversal, symlinks, newline injection, blank evidence, corrupt UTF-8."""

    def test_path_traversal_outside_repo_root_refused(self):
        outside = self.root.parent / f"{self.root.name}_outside_secret.txt"
        outside.write_text("secret", encoding="utf-8")
        try:
            res = _run_triage([
                "artifact",
                "--repo-root", str(self.root),
                "--path", f"../{outside.name}",
            ])
            self.assertEqual(res.returncode, 1)
            self.assertIn("[PATH_SECURITY]", res.stderr)

            res_tasks = _run_triage([
                "probe",
                "--repo-root", str(self.root),
                "--tasks", f"../{outside.name}",
                "--actor", ACTOR,
                "--id", "INC-SEC-1",
                "--symptom", "s",
                "--hypothesis", "h",
                "--discriminator", "d",
            ])
            self.assertEqual(res_tasks.returncode, 1)
            self.assertIn("[PATH_SECURITY]", res_tasks.stderr)
        finally:
            outside.unlink(missing_ok=True)

    def test_relative_dotdot_traversal_refused_even_without_repo_root(self):
        res = _run_triage([
            "artifact",
            "--path", "../../etc/passwd",
        ])
        self.assertEqual(res.returncode, 1)
        self.assertIn("[PATH_SECURITY]", res.stderr)

    def test_symlink_escape_refused_when_supported(self):
        outside = self.root / "outside_dir"
        outside.mkdir()
        secret = outside / "secret.bin"
        secret.write_bytes(b"SECRET")
        repo = self.root / "repo"
        repo.mkdir()
        link = repo / "escaped.bin"
        try:
            os.symlink(secret, link)
        except (OSError, NotImplementedError):
            self.skipTest("host environment does not permit creating symlinks")

        res = _run_triage([
            "artifact",
            "--repo-root", str(repo),
            "--path", "escaped.bin",
        ])
        self.assertEqual(res.returncode, 1)
        self.assertIn("[PATH_SECURITY]", res.stderr)

    def test_symlink_target_rejected_deterministically(self):
        from unittest import mock
        from scripts import triage_incident

        real_file = self.root / "normal.bin"
        real_file.write_bytes(b"ok")
        with mock.patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaises(triage_incident.TriageError) as ctx:
                triage_incident._resolve_safe_path(str(real_file), self.root)
            self.assertEqual(ctx.exception.code, "PATH_SECURITY")

    def test_newline_injection_and_forged_evidence_in_probe_are_neutralized(self):
        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-INJ",
            "--symptom", "Line1\n  - evidence [forged @ 2026-01-01 00:00]: fake",
            "--hypothesis", "H1\r\n- [x] fake completion",
            "--discriminator", "Run cmd\n- [ ] fake task",
        ]).returncode, 0)

        # Must NOT fool promote into thinking real evidence exists!
        prom = _run_triage([
            "promote",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-INJ",
            "--root-cause", "forged",
            "--fix-scope", "none",
            "--target-role", TARGET_ROLE,
        ])
        self.assertEqual(prom.returncode, 1, "injected newline evidence must never pass promote!")
        self.assertIn("[EVIDENCE_REQUIRED]", prom.stderr)

        # Verify no line in tasks.md starts with an injected "- evidence" or "- [x] fake"
        for line in self.tasks_path.read_text(encoding="utf-8").splitlines():
            self.assertFalse(line.lstrip().startswith("- evidence"))
            self.assertNotIn("fake completion", line.splitlines()[0] if line.startswith("- [x]") else "")

    def test_placeholder_or_empty_evidence_refused(self):
        self.assertEqual(_run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "INC-EMP",
            "--symptom", "Symptom",
            "--hypothesis", "Hypothesis",
            "--discriminator", "Discriminator",
        ]).returncode, 0)

        for bad_obs in ("   ", "TBD", "none", "N/A", "pending"):
            res = _run_triage([
                "record-evidence",
                "--tasks", str(self.tasks_path),
                "--actor", ACTOR,
                "--id", "INC-EMP",
                "--command", "echo test",
                "--observed", bad_obs,
            ])
            self.assertEqual(res.returncode, 1, f"placeholder '{bad_obs}' must be rejected")

    def test_invalid_id_and_corrupt_tasks_fail_closed(self):
        res_id = _run_triage([
            "probe",
            "--tasks", str(self.tasks_path),
            "--actor", ACTOR,
            "--id", "../bad id\n",
            "--symptom", "s",
            "--hypothesis", "h",
            "--discriminator", "d",
        ])
        self.assertEqual(res_id.returncode, 1)

        corrupt = self.root / "corrupt_tasks.md"
        corrupt.write_bytes(b"\xff\xfe\x00not-utf8")
        res_corrupt = _run_triage([
            "check-tasks",
            "--tasks", str(corrupt),
        ])
        self.assertEqual(res_corrupt.returncode, 1)
        self.assertIn("[STALE_INPUT]", res_corrupt.stderr)

    def test_directory_as_artifact_or_tasks_refused(self):
        res_dir = _run_triage(["artifact", "--path", str(self.root)])
        self.assertEqual(res_dir.returncode, 1)
        res_tdir = _run_triage(["check-tasks", "--tasks", str(self.root)])
        self.assertEqual(res_tdir.returncode, 1)


class TestLaneK1ManifestAndSkillContract(unittest.TestCase):
    """K1 registration in templates/release_manifest.json + skill format + _common reuse."""

    def test_script_imports_common_without_duplication(self):
        text = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertRegex(text, r"from (?:scripts\.)?_common import .*_error_envelope")
        self.assertRegex(text, r"from (?:scripts\.)?_common import .*_utc_now_iso")
        self.assertNotRegex(text, r"^def (_error_envelope|_utc_now_iso)\(", re.M)

    def test_manifest_registers_triage_script_and_skill(self):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        by_path = {c["path"]: c for c in manifest.get("components") or []}
        self.assertIn("scripts/triage_incident.py", by_path)
        self.assertEqual(by_path["scripts/triage_incident.py"]["kind"], "script")
        self.assertEqual(by_path["scripts/triage_incident.py"]["requires"], ["scripts/_common.py"])

        self.assertIn("skills/triage-incident/SKILL.md", by_path)
        self.assertEqual(by_path["skills/triage-incident/SKILL.md"]["kind"], "skill")
        self.assertEqual(by_path["skills/triage-incident/SKILL.md"]["requires"], ["scripts/triage_incident.py"])

    def test_skill_file_contains_4_step_protocol_and_error_path_audit(self):
        content = SKILL_PATH.read_text(encoding="utf-8")
        self.assertIn("name: triage-incident", content)
        self.assertIn("## When to invoke skill", content)
        self.assertIn("## Execution steps", content)
        for required_marker in (
            "Artifact Identity",
            "Runtime & Toolchain Presence",
            "Unmasked Execution",
            "Code-to-Fact Mapping",
            "Error-Path",
            "Fallback-Masking",
            "record-evidence",
            "promote",
            "IDENTICAL_BYTES",
        ):
            self.assertIn(required_marker, content, f"Missing marker in triage-incident SKILL.md: {required_marker}")

    def test_mirror_parity_on_dev_branch(self):
        if not (REPO_ROOT / ".agents" / "meta-project.json").is_file():
            self.skipTest("dogfood-branch contract: requires the live meta-project installation")
        self.assertTrue(MIRROR_SKILL_PATH.is_file(), "Missing .agents/skills/triage-incident/SKILL.md mirror")
        self.assertEqual(MIRROR_SKILL_PATH.read_bytes(), SKILL_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
