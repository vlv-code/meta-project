#!/usr/bin/env python3
"""Canonical domain test suite for Meta-Project thin hooks ecosystem.

Covers:
- hooks/dispatch.py: unified stdlib event dispatcher for all 6 harnesses
- hooks/install.py: idempotent installer, dry-run live verifier, clean uninstaller
- hooks/hooks.json: native Claude Code plugin manifest
- hooks/README.md: protocol documentation

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class HooksTestBase(unittest.TestCase):
    """Base setup creating a temporary meta-project repository with boundaries."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp)
        self.agents_dir = self.root / ".agents"
        self.pk_dir = self.agents_dir / "project_knowledge"
        self.pk_dir.mkdir(parents=True, exist_ok=True)

        # Baseline boundaries.md
        boundaries_content = """# Boundaries

## Green Zone (Unrestricted)
- `tests/**`
- `docs/**`
- `README.md`
- `hooks/**`

## Yellow Zone (Governed)
- `scripts/**`
- `skills/**`
- `.agents/**`

## Red Zone (Protected / Sanitized)
- `scripts/check_boundaries.py`
- `tests/test_integrity.py`
- `.agents/project_knowledge/boundaries.md`
- `LICENSE`
"""
        (self.pk_dir / "boundaries.md").write_text(boundaries_content, encoding="utf-8")
        (self.root / "AGENTS.md").write_text("# Passport\n", encoding="utf-8")

        # Create dummy script files for boundaries and helpers
        (self.root / "scripts").mkdir(parents=True, exist_ok=True)
        (self.root / "scripts" / "check_boundaries.py").write_text("# check_boundaries\n", encoding="utf-8")
        (self.root / "scripts" / "verify_identity.py").write_text("# verify_identity\n", encoding="utf-8")
        (self.root / "README.md").write_text("# Readme\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("MIT\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_dispatch(self, args: list[str], payload: dict | str, cwd: Path | None = None, env: dict | None = None) -> tuple[int, str, str]:
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
        cmd = [sys.executable, str(REPO_ROOT / "hooks" / "dispatch.py"), *args]
        input_data = json.dumps(payload) if isinstance(payload, dict) else payload
        proc = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            cwd=str(cwd or self.root),
            env=run_env,
        )
        return proc.returncode, proc.stdout, proc.stderr


class TestHooksDispatchPreToolUse(HooksTestBase):
    """Verification of hooks/dispatch.py pre-tool-use across all 6 harnesses."""

    def test_silent_noop_outside_meta_project_repo(self):
        empty_dir = Path(tempfile.mkdtemp())
        try:
            payload = {"tool_name": "write_file", "tool_input": {"path": "anything.py"}}
            for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
                rc, out, err = self._run_dispatch(["--harness", harness, "--event", "pre-tool-use"], payload, cwd=empty_dir)
                self.assertEqual(rc, 0, f"Expected rc=0 for {harness} outside repo")
                # Must be valid json or empty
                if out.strip():
                    data = json.loads(out)
                    if harness in ("claude-code", "zcode"):
                        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")
                    elif harness == "cursor":
                        self.assertEqual(data["permission"], "allow")
                    elif harness == "gemini":
                        self.assertEqual(data["decision"], "allow")
                    elif harness == "copilot":
                        self.assertEqual(data["permissionDecision"], "allow")
                    elif harness == "codex":
                        self.assertEqual(data["decision"], "allow")
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_green_path_allowed_across_all_harnesses(self):
        payload = {"tool_name": "write_file", "tool_input": {"path": "README.md"}}
        for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(["--harness", harness, "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 0, f"Failed for {harness}: err={err}")
            data = json.loads(out)
            if harness in ("claude-code", "zcode"):
                self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")
            elif harness == "cursor":
                self.assertEqual(data["permission"], "allow")
            elif harness == "gemini":
                self.assertEqual(data["decision"], "allow")
            elif harness == "copilot":
                self.assertEqual(data["permissionDecision"], "allow")
            elif harness == "codex":
                self.assertEqual(data["decision"], "allow")

    def test_read_only_tools_always_allowed_even_in_red_zone_adr_15(self):
        """ADR #15: Read-only operations must never be blocked, even in Red Zone."""
        red_targets = [
            ".agents/project_knowledge/boundaries.md",
            "scripts/check_boundaries.py",
            "tests/test_integrity.py",
            "LICENSE",
        ]
        read_tools = [
            "read",
            "read_file",
            "view_file",
            "getfile",
            "view",
            "grep",
            "grep_search",
            "glob",
            "find_by_name",
            "list_dir",
            "ls",
            "search",
        ]
        for target in red_targets:
            for rtool in ["Read", "read_file"]:
                payload = {"tool_name": rtool, "tool_input": {"path": target}}
                for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
                    rc, out, err = self._run_dispatch(["--harness", harness, "--event", "pre-tool-use"], payload)
                    self.assertEqual(rc, 0, f"Read tool '{rtool}' on '{target}' failed for {harness}: {err}")
                    data = json.loads(out)
                    if harness in ("claude-code", "zcode"):
                        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")
                    elif harness == "cursor":
                        self.assertEqual(data["permission"], "allow")
                    elif harness == "gemini":
                        self.assertEqual(data["decision"], "allow")
                    elif harness == "copilot":
                        self.assertEqual(data["permissionDecision"], "allow")
                    elif harness == "codex":
                        self.assertEqual(data["decision"], "allow")

        # Test full spectrum of read tools on a Red Zone file
        for rtool in read_tools:
            payload = {"tool_name": rtool, "tool_input": {"path": "scripts/check_boundaries.py"}}
            rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 0, f"Tool '{rtool}' failed on Red Zone: {err}")
            data = json.loads(out)
            self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_yellow_path_allowed_default(self):
        payload = {"tool_name": "Edit", "tool_input": {"file_path": "scripts/inspect_meta_project.py"}}
        for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(["--harness", harness, "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 0)
            data = json.loads(out)
            if harness in ("claude-code", "zcode"):
                self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")
            elif harness == "cursor":
                self.assertEqual(data["permission"], "allow")
            elif harness == "gemini":
                self.assertEqual(data["decision"], "allow")

    def test_red_path_denied_default_fail_closed(self):
        payload = {"tool_name": "write_file", "tool_input": {"path": "scripts/check_boundaries.py"}}
        for harness in ["claude-code", "zcode", "cursor", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(["--harness", harness, "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 2, f"Expected rc=2 for {harness}")
            data = json.loads(out)
            if harness in ("claude-code", "zcode"):
                self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "deny")
                self.assertIn("Red Zone", data["hookSpecificOutput"]["permissionDecisionReason"])
            elif harness == "cursor":
                self.assertEqual(data["permission"], "deny")
            elif harness == "copilot":
                self.assertEqual(data["permissionDecision"], "deny")
            elif harness == "codex":
                self.assertEqual(data["decision"], "block")

        # Gemini returns rc=0 with decision="deny"
        rc, out, err = self._run_dispatch(["--harness", "gemini", "--event", "pre-tool-use"], payload)
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "deny")
        self.assertIn("Red Zone", data["reason"])

    def test_red_policy_ask_interactive_on_supported_and_fail_closed_on_others(self):
        payload = {"tool_name": "write_file", "tool_input": {"path": "LICENSE"}}

        # Supported: claude-code, zcode, gemini -> ask
        for harness in ["claude-code", "zcode"]:
            rc, out, err = self._run_dispatch(
                ["--harness", harness, "--event", "pre-tool-use", "--red-policy", "ask"],
                payload,
            )
            self.assertEqual(rc, 0)
            data = json.loads(out)
            self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "ask")

        rc, out, err = self._run_dispatch(
            ["--harness", "gemini", "--event", "pre-tool-use", "--red-policy", "ask"],
            payload,
        )
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "ask")

        # Fail-closed degradation to deny on cursor, copilot, codex even with --red-policy ask
        for harness in ["cursor", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(
                ["--harness", harness, "--event", "pre-tool-use", "--red-policy", "ask"],
                payload,
            )
            self.assertEqual(rc, 2, f"Expected fail-closed rc=2 on {harness} with --red-policy ask")
            data = json.loads(out)
            if harness == "cursor":
                self.assertEqual(data["permission"], "deny")
            elif harness == "copilot":
                self.assertEqual(data["permissionDecision"], "deny")
            elif harness == "codex":
                self.assertEqual(data["decision"], "block")

    def test_red_zone_environment_override(self):
        payload = {"tool_name": "write_file", "tool_input": {"path": "LICENSE"}}
        env = {"META_PROJECT_ALLOW_RED_ZONE": "1"}
        for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(
                ["--harness", harness, "--event", "pre-tool-use"],
                payload,
                env=env,
            )
            self.assertEqual(rc, 0, f"Expected rc=0 with env override on {harness}")
            data = json.loads(out)
            if harness in ("claude-code", "zcode"):
                self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")
            elif harness == "cursor":
                self.assertEqual(data["permission"], "allow")
            elif harness == "gemini":
                self.assertEqual(data["decision"], "allow")

    def test_path_key_normalization_candidates(self):
        candidates = [
            {"file_path": "README.md"},
            {"path": "README.md"},
            {"TargetFile": "README.md"},
            {"target_file": "README.md"},
            {"AbsolutePath": str(self.root / "README.md")},
            {"Path": "README.md"},
            {"file": "README.md"},
        ]
        for c in candidates:
            payload = {"tool_name": "edit", "tool_input": c}
            rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 0, f"Candidate key {c} failed: {err}")
            data = json.loads(out)
            self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_codex_apply_patch_multi_file_most_restrictive_wins(self):
        # 1 Green (README.md) + 1 Red (LICENSE) -> must be blocked
        patch_text = """*** Update File: README.md
--- README.md
+++ README.md
@@ -1 +1 @@
-# Readme
+# Readme Updated
*** Update File: LICENSE
--- LICENSE
+++ LICENSE
@@ -1 +1 @@
-MIT
+Apache
"""
        payload = {"tool_name": "apply_patch", "tool_input": {"patch": patch_text}}
        rc, out, err = self._run_dispatch(["--harness", "codex", "--event", "pre-tool-use"], payload)
        self.assertEqual(rc, 2)
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")

        # Only Green files -> allowed
        green_patch = """*** Update File: README.md
--- README.md
+++ README.md
@@ -1 +1 @@
-# Readme
+# Readme Green
"""
        payload_green = {"tool_name": "apply_patch", "tool_input": {"patch": green_patch}}
        rc, out, err = self._run_dispatch(["--harness", "codex", "--event", "pre-tool-use"], payload_green)
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "allow")

    def test_gemini_strict_stdout_purity(self):
        payload = {"tool_name": "write_file", "tool_input": {"path": "scripts/check_boundaries.py"}}
        rc, out, err = self._run_dispatch(["--harness", "gemini", "--event", "pre-tool-use"], payload)
        self.assertEqual(rc, 0)
        out_stripped = out.strip()
        self.assertTrue(out_stripped.startswith("{"), "Gemini stdout must start with {")
        self.assertTrue(out_stripped.endswith("}"), "Gemini stdout must end with }")
        # Ensure it is exactly one JSON object
        data = json.loads(out_stripped)
        self.assertIn("decision", data)

    def test_fail_closed_on_corrupted_boundaries_or_malformed_json(self):
        # Malformed JSON payload
        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], "NOT_JSON")
        self.assertEqual(rc, 2)
        data = json.loads(out)
        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "deny")

        # Corrupted boundaries.md inside repo
        (self.pk_dir / "boundaries.md").write_text("", encoding="utf-8")  # empty or invalid
        payload = {"tool_name": "write_file", "tool_input": {"path": "README.md"}}
        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
        self.assertEqual(rc, 2)
        data = json.loads(out)
        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "deny")


class TestHooksDispatchReadGate(HooksTestBase):
    """Verification of opt-in --with-read-gate and post-tool-use logging."""

    def test_read_gate_blocks_yellow_until_boundaries_read(self):
        session_id = "test-session-123"
        payload_write = {
            "session_id": session_id,
            "tool_name": "write_file",
            "tool_input": {"path": "scripts/verify_identity.py"},
        }

        # 1. First write attempt without having read boundaries.md -> DENY
        rc, out, err = self._run_dispatch(
            ["--harness", "claude-code", "--event", "pre-tool-use", "--with-read-gate"],
            payload_write,
        )
        self.assertEqual(rc, 2)
        data = json.loads(out)
        self.assertEqual(data["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn("boundaries.md", data["hookSpecificOutput"]["permissionDecisionReason"])

        # 2. Simulate post-tool-use read of boundaries.md
        payload_read = {
            "session_id": session_id,
            "tool_name": "read_file",
            "tool_input": {"path": ".agents/project_knowledge/boundaries.md"},
        }
        rc_read, out_read, _ = self._run_dispatch(
            ["--harness", "claude-code", "--event", "post-tool-use", "--with-read-gate"],
            payload_read,
        )
        self.assertEqual(rc_read, 0)

        # 3. Second write attempt -> ALLOW
        rc2, out2, err2 = self._run_dispatch(
            ["--harness", "claude-code", "--event", "pre-tool-use", "--with-read-gate"],
            payload_write,
        )
        self.assertEqual(rc2, 0, f"Expected allow after read: {err2}")
        data2 = json.loads(out2)
        self.assertEqual(data2["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_e2e_read_gate_lifecycle_no_deadlock(self):
        """ADR #15: PreToolUse on boundaries.md must succeed so agent can read boundaries.md to unblock yellow writes."""
        session_id = "e2e-no-deadlock-session"

        # 1. PreToolUse on boundaries.md (Red Zone) with tool_name="Read" -> MUST BE ALLOWED (no deadlock)
        payload_read_pre = {
            "session_id": session_id,
            "tool_name": "Read",
            "tool_input": {"path": ".agents/project_knowledge/boundaries.md"},
        }
        rc_pre, out_pre, err_pre = self._run_dispatch(
            ["--harness", "claude-code", "--event", "pre-tool-use", "--with-read-gate"],
            payload_read_pre,
        )
        self.assertEqual(rc_pre, 0, f"PreToolUse on boundaries.md failed: {err_pre}")
        d_pre = json.loads(out_pre)
        self.assertEqual(d_pre["hookSpecificOutput"]["permissionDecision"], "allow")

        # 2. PostToolUse on boundaries.md with tool_name="Read" -> records in journal
        rc_post, out_post, _ = self._run_dispatch(
            ["--harness", "claude-code", "--event", "post-tool-use", "--with-read-gate"],
            payload_read_pre,
        )
        self.assertEqual(rc_post, 0)

        # 3. PreToolUse on Yellow file with tool_name="Edit" -> ALLOWED because boundaries.md is in journal
        payload_write = {
            "session_id": session_id,
            "tool_name": "Edit",
            "tool_input": {"path": "scripts/inspect_meta_project.py"},
        }
        rc_w, out_w, err_w = self._run_dispatch(
            ["--harness", "claude-code", "--event", "pre-tool-use", "--with-read-gate"],
            payload_write,
        )
        self.assertEqual(rc_w, 0, f"Yellow write failed after reading boundaries: {err_w}")
        d_w = json.loads(out_w)
        self.assertEqual(d_w["hookSpecificOutput"]["permissionDecision"], "allow")


class TestHooksDispatchSessionStart(HooksTestBase):
    """Verification of hooks/dispatch.py session-start event."""

    def test_session_start_read_only_and_budget_le_4000(self):
        # Create minimal meta-project.json and tasks.md
        meta_json = {
            "schema_version": "1.0",
            "project_id": "test-proj",
            "installations": {"ag-main": {"harness": "antigravity", "status": "active"}},
        }
        (self.agents_dir / "meta-project.json").write_text(json.dumps(meta_json), encoding="utf-8")
        (self.pk_dir / "tasks.md").write_text("# Active Tasks\n- [ ] Unverified hypothesis: bug X\n", encoding="utf-8")

        for harness in ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]:
            rc, out, err = self._run_dispatch(["--harness", harness, "--event", "session-start"], {})
            self.assertEqual(rc, 0, f"Failed for {harness}: {err}")
            data = json.loads(out)
            context = ""
            if harness in ("claude-code", "zcode"):
                context = data["hookSpecificOutput"]["additionalContext"]
            elif harness == "gemini":
                context = data["systemMessage"]
            else:
                context = data["additionalContext"]

            self.assertTrue(len(context) > 0, f"Context empty for {harness}")
            self.assertLessEqual(len(context), 4000, f"Context exceeded 4000 chars for {harness}")


class TestHooksInstallLifecycle(HooksTestBase):
    """Verification of hooks/install.py install, verify, and uninstall."""

    def _run_install(self, args: list[str]) -> tuple[int, str, str]:
        cmd = [sys.executable, str(REPO_ROOT / "hooks" / "install.py"), *args, "--repo-root", str(self.root)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr

    def test_install_verify_uninstall_across_harnesses(self):
        for harness in ["claude-code", "cursor", "gemini", "copilot", "codex"]:
            # 1. Install
            rc, out, err = self._run_install(["install", "--harness", harness, "--no-git-hook"])
            self.assertEqual(rc, 0, f"Install failed for {harness}: {err}")

            # 2. Verify
            rc_v, out_v, err_v = self._run_install(["verify", "--harness", harness])
            self.assertEqual(rc_v, 0, f"Verify failed for {harness}: {err_v}")

            # 3. Uninstall
            rc_u, out_u, err_u = self._run_install(["uninstall", "--harness", harness])
            self.assertEqual(rc_u, 0, f"Uninstall failed for {harness}: {err_u}")

    def test_install_preserves_pre_existing_user_hooks(self):
        claude_dir = self.root / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        user_config = {
            "my_custom_key": 123,
            "hooks": {
                "PreToolUse": [{"command": "echo user_pre"}],
                "PostToolUse": [{"command": "echo user_post"}],
            },
        }
        (claude_dir / "settings.json").write_text(json.dumps(user_config), encoding="utf-8")

        # Install claude-code
        rc, out, err = self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        self.assertEqual(rc, 0)

        # Check that user hooks and custom keys are preserved
        updated = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(updated["my_custom_key"], 123)
        flat_commands = [h.get("command") for h in updated["hooks"]["PreToolUse"] if "command" in h]
        nested_commands = [
            sh.get("command")
            for h in updated["hooks"]["PreToolUse"]
            if "hooks" in h
            for sh in h["hooks"]
        ]
        self.assertIn("echo user_pre", flat_commands)
        self.assertTrue(any("hooks/dispatch.py" in cmd for cmd in nested_commands if cmd))

        # Uninstall claude-code
        rc_u, _, _ = self._run_install(["uninstall", "--harness", "claude-code"])
        self.assertEqual(rc_u, 0)

        restored = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(restored["my_custom_key"], 123)
        restored_flat = [h.get("command") for h in restored.get("hooks", {}).get("PreToolUse", []) if "command" in h]
        restored_nested = [
            sh.get("command")
            for h in restored.get("hooks", {}).get("PreToolUse", [])
            if "hooks" in h
            for sh in h["hooks"]
        ]
        self.assertIn("echo user_pre", restored_flat)
        self.assertFalse(any("hooks/dispatch.py" in cmd for cmd in restored_nested if cmd))

    def test_install_fails_closed_on_corrupted_json(self):
        cursor_dir = self.root / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        (cursor_dir / "hooks.json").write_text("CORRUPTED_NOT_JSON{", encoding="utf-8")

        rc, out, err = self._run_install(["install", "--harness", "cursor", "--no-git-hook"])
        self.assertNotEqual(rc, 0, "Install must fail closed on corrupted JSON")
        # Content must not be overwritten
        self.assertEqual((cursor_dir / "hooks.json").read_text(encoding="utf-8"), "CORRUPTED_NOT_JSON{")

    def test_hooks_manifest_nested_schema(self):
        manifest_path = REPO_ROOT / "hooks" / "hooks.json"
        self.assertTrue(manifest_path.is_file())
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        hooks = data.get("hooks", {})

        # SessionStart
        start_entries = hooks.get("SessionStart", [])
        self.assertEqual(len(start_entries), 1)
        self.assertIn("hooks", start_entries[0])
        self.assertEqual(start_entries[0]["hooks"][0]["type"], "command")
        self.assertIn("dispatch.py", start_entries[0]["hooks"][0]["command"])

        # PreToolUse
        pre_entries = hooks.get("PreToolUse", [])
        self.assertGreaterEqual(len(pre_entries), 1)
        edit_entries = [e for e in pre_entries if e.get("matcher") == "Edit|Write|MultiEdit"]
        self.assertEqual(len(edit_entries), 1)
        self.assertIn("hooks", edit_entries[0])
        self.assertEqual(edit_entries[0]["hooks"][0]["type"], "command")
        self.assertIn("dispatch.py", edit_entries[0]["hooks"][0]["command"])

    def test_install_nested_schemas_and_attributes(self):
        # 1. Claude Code
        rc, _, err = self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Claude install failed: {err}")
        claude_cfg = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        pre_claude = claude_cfg["hooks"]["PreToolUse"]
        self.assertEqual(pre_claude[0]["matcher"], "Edit|Write|MultiEdit")
        self.assertEqual(pre_claude[0]["hooks"][0]["type"], "command")
        self.assertIn("hooks/dispatch.py", pre_claude[0]["hooks"][0]["command"])
        start_claude = claude_cfg["hooks"]["SessionStart"]
        self.assertEqual(start_claude[0]["hooks"][0]["type"], "command")
        self.assertNotIn("PostToolUse", claude_cfg["hooks"], "PostToolUse must NOT be created when with_read_gate=False")

        # 2. Gemini
        rc, _, err = self._run_install(["install", "--harness", "gemini", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Gemini install failed: {err}")
        gemini_cfg = json.loads((self.root / ".gemini" / "settings.json").read_text(encoding="utf-8"))
        before_gemini = gemini_cfg["hooks"]["BeforeTool"]
        self.assertEqual(before_gemini[0]["matcher"], "write_file|replace|replace_string|edit_file")
        self.assertEqual(before_gemini[0]["hooks"][0]["type"], "command")
        self.assertEqual(before_gemini[0]["hooks"][0]["name"], "meta-project-boundary-gate")
        start_gemini = gemini_cfg["hooks"]["SessionStart"]
        self.assertEqual(start_gemini[0]["matcher"], "startup")
        self.assertEqual(start_gemini[0]["hooks"][0]["name"], "meta-project-session-start")
        self.assertNotIn("AfterTool", gemini_cfg["hooks"], "AfterTool must NOT be created when with_read_gate=False")

        # 3. Codex
        rc, _, err = self._run_install(["install", "--harness", "codex", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Codex install failed: {err}")
        codex_cfg = json.loads((self.root / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        pre_codex = codex_cfg["hooks"]["PreToolUse"]
        self.assertEqual(pre_codex[0]["matcher"], "apply_patch|Write|Edit")
        self.assertEqual(pre_codex[0]["hooks"][0]["type"], "command")
        start_codex = codex_cfg["hooks"]["SessionStart"]
        self.assertEqual(start_codex[0]["hooks"][0]["type"], "command")

        # 4. Copilot
        rc, _, err = self._run_install(["install", "--harness", "copilot", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Copilot install failed: {err}")
        copilot_cfg = json.loads((self.root / ".github" / "hooks" / "meta-project.json").read_text(encoding="utf-8"))
        for ev in ["preToolUse", "sessionStart"]:
            for entry in copilot_cfg["hooks"][ev]:
                self.assertEqual(entry.get("type"), "command", f"Copilot entry missing type='command' in {ev}")
                self.assertIn("bash", entry)
                self.assertIn("powershell", entry)

        # 5. Cursor
        rc, _, err = self._run_install(["install", "--harness", "cursor", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Cursor install failed: {err}")
        cursor_cfg = json.loads((self.root / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
        pre_cursor = cursor_cfg["hooks"]["preToolUse"]
        self.assertEqual(pre_cursor[0]["matcher"], "Write|Edit|StrReplace")
        self.assertTrue(pre_cursor[0].get("failClosed"))
        self.assertNotIn("postToolUse", cursor_cfg["hooks"], "postToolUse must NOT be created when with_read_gate=False")

    def test_install_with_read_gate_adds_post_tool_use(self):
        rc, _, err = self._run_install(["install", "--harness", "claude-code", "--with-read-gate", "--no-git-hook"])
        self.assertEqual(rc, 0)
        claude_cfg = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertIn("PostToolUse", claude_cfg["hooks"])
        post_entry = claude_cfg["hooks"]["PostToolUse"][0]
        self.assertEqual(post_entry["matcher"], "Read")
        self.assertEqual(post_entry["hooks"][0]["type"], "command")
        self.assertIn("--with-read-gate", post_entry["hooks"][0]["command"])

    def test_preserve_neighbor_user_hook_inside_same_matcher(self):
        claude_dir = self.root / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        user_cfg = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Edit|Write|MultiEdit",
                        "hooks": [
                            {"type": "command", "command": "echo neighbor_user_hook"}
                        ],
                    }
                ]
            }
        }
        (claude_dir / "settings.json").write_text(json.dumps(user_cfg), encoding="utf-8")

        # Install claude-code
        rc, _, err = self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        self.assertEqual(rc, 0)

        cfg_after_install = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
        pre_hooks = cfg_after_install["hooks"]["PreToolUse"][0]["hooks"]
        commands = [h.get("command") for h in pre_hooks]
        self.assertIn("echo neighbor_user_hook", commands)
        self.assertTrue(any("hooks/dispatch.py" in cmd for cmd in commands if cmd))

        # Uninstall claude-code
        rc_u, _, _ = self._run_install(["uninstall", "--harness", "claude-code"])
        self.assertEqual(rc_u, 0)

        cfg_after_uninstall = json.loads((claude_dir / "settings.json").read_text(encoding="utf-8"))
        pre_hooks_restored = cfg_after_uninstall["hooks"]["PreToolUse"][0]["hooks"]
        restored_commands = [h.get("command") for h in pre_hooks_restored]
        self.assertIn("echo neighbor_user_hook", restored_commands)
        self.assertFalse(any("hooks/dispatch.py" in cmd for cmd in restored_commands if cmd))

    def test_install_all_no_collision_on_claude_settings(self):
        rc, _, err = self._run_install(["install", "--harness", "all", "--no-git-hook"])
        self.assertEqual(rc, 0, f"install all failed: {err}")

        claude_cfg = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
        pre_list = claude_cfg["hooks"]["PreToolUse"]
        # Exactly 1 matcher block for Edit|Write|MultiEdit and 1 for Bash without duplication
        edit_matchers = [b for b in pre_list if b.get("matcher") == "Edit|Write|MultiEdit"]
        self.assertEqual(len(edit_matchers), 1)
        meta_hooks = [h for h in edit_matchers[0]["hooks"] if "hooks/dispatch.py" in str(h.get("command", ""))]
        self.assertEqual(len(meta_hooks), 1, "Expected exactly 1 meta-project hook entry without duplicate/collision")

        bash_matchers = [b for b in pre_list if b.get("matcher") == "Bash"]
        self.assertEqual(len(bash_matchers), 1)

    def test_verify_includes_probe_4_adr_15(self):
        rc_i, _, _ = self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        self.assertEqual(rc_i, 0)

        rc_v, out_v, err_v = self._run_install(["verify", "--harness", "claude-code"])
        self.assertEqual(rc_v, 0, f"Verify failed: {err_v}")

        rc_z, out_z, _ = self._run_install(["verify", "--harness", "zcode"])
        self.assertEqual(rc_z, 0)
        self.assertIn("Confirm live hook execution inside an actual ZCode Desktop session", out_z)


class TestWaveZ32SessionStart(HooksTestBase):
    """Wave Z3.2: SessionStart target_harness detection, runtime installation resolution, triage, compact, grounding."""

    def test_session_start_detects_zcode_host_and_active_installation(self):
        (self.root / "AGENTS.md").write_text("# Project Passport: Test\n## 1. Concept\nNorth Stars\n", encoding="utf-8")
        meta_json = {
            "schema_version": "1.1.0",
            "project_id": "test-zcode-project",
            "installations": {
                "zc-main": {"harness_id": "zcode", "status": "active"}
            },
        }
        (self.agents_dir / "meta-project.json").write_text(json.dumps(meta_json), encoding="utf-8")

        # Simulate real ZCode desktop environment markers
        env = {
            "ZCODE_PROJECT_DIR": str(self.root),
            "ZCODE_SESSION_ID": "zcode-session-999",
        }
        rc, out, err = self._run_dispatch(["--harness", "zcode", "--event", "session-start"], {}, env=env)
        self.assertEqual(rc, 0, f"SessionStart failed: {err}")
        data = json.loads(out)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("State=HEALTHY_REGISTERED", ctx)
        self.assertIn("Installation=zc-main", ctx)
        self.assertNotIn("unbound", ctx)

    def test_session_start_triage_incident_parsing_and_compact_memory(self):
        (self.root / "AGENTS.md").write_text("# Project Passport: Test\n## 1. Concept\nNorth Stars\n", encoding="utf-8")
        meta_json = {
            "schema_version": "1.1.0",
            "project_id": "test-project",
            "installations": {"ag-main": {"harness_id": "antigravity", "status": "active"}},
        }
        (self.agents_dir / "meta-project.json").write_text(json.dumps(meta_json), encoding="utf-8")

        # Tasks with structured PROBE
        tasks_content = """# Current and Active Project Tasks
- [?] PROBE: DIAG-042 investigate silent failure in build container
  - hypothesis: path issue in container
"""
        (self.pk_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

        # Observations with >20 rows to trigger compact_observations
        obs_rows = ["# Observations", "", "| Date | Category | Path | Issue | Solution |", "| :--- | :--- | :--- | :--- | :--- |"]
        for i in range(25):
            obs_rows.append(f"| 2026-11-25 | [test] | path{i}.py | issue {i} | solution {i} |")
        (self.pk_dir / "observations.md").write_text("\n".join(obs_rows) + "\n", encoding="utf-8")

        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "session-start"], {})
        self.assertEqual(rc, 0, f"SessionStart failed: {err}")
        data = json.loads(out)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("DIAG-042", ctx)
        self.assertIn("compact_memory.py", ctx)

    def test_session_start_post_compaction_grounding(self):
        meta_json = {
            "schema_version": "1.1.0",
            "project_id": "test-project",
            "installations": {"ag-main": {"harness": "antigravity", "status": "active"}},
        }
        (self.agents_dir / "meta-project.json").write_text(json.dumps(meta_json), encoding="utf-8")
        tasks_content = """# Tasks
- [?] PROBE: DIAG-099 open probe without evidence
"""
        (self.pk_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

        payload = {"source": "compact"}
        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "session-start"], payload)
        self.assertEqual(rc, 0)
        data = json.loads(out)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Post-Compaction Grounding", ctx)
        self.assertIn("FACTS vs HYPOTHESES", ctx)


class TestWaveZ32BashGuard(HooksTestBase):
    """Wave Z3.2: PreToolUse narrow anti-bypass Bash guard."""

    def test_bash_git_commit_no_verify_denied(self):
        bypass_cmds = [
            "git commit --no-verify -m 'skip checks'",
            "git commit -n -m 'skip'",
            "git commit -m 'msg' --no-verify",
        ]
        for cmd in bypass_cmds:
            payload = {"tool_name": "bash", "tool_input": {"command": cmd}}
            rc, out, _ = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 2, f"Expected deny on {cmd}")
            d = json.loads(out)
            self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "deny")

            # Gemini harness returns rc=0 with decision="deny"
            rc_g, out_g, _ = self._run_dispatch(["--harness", "gemini", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc_g, 0)
            d_g = json.loads(out_g)
            self.assertEqual(d_g["decision"], "deny")

    def test_bash_git_push_force_denied(self):
        force_cmds = [
            "git push --force origin main",
            "git push -f",
            "git push --force-with-lease origin dev",
        ]
        for cmd in force_cmds:
            payload = {"tool_name": "bash", "tool_input": {"command": cmd}}
            rc, out, _ = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 2, f"Expected deny on {cmd}")
            d = json.loads(out)
            self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_bash_safe_commands_allowed(self):
        safe_cmds = [
            "git status",
            "git diff LICENSE",
            "python -m unittest discover",
            "pytest tests/",
            "cat README.md",
            "echo hello",
        ]
        for cmd in safe_cmds:
            payload = {"tool_name": "bash", "tool_input": {"command": cmd}}
            rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload)
            self.assertEqual(rc, 0, f"Expected allow on safe command '{cmd}': {err}")
            d = json.loads(out)
            self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_bash_override_allows_bypass(self):
        payload = {"tool_name": "bash", "tool_input": {"command": "git commit --no-verify -m 'override'"}}
        env = {"META_PROJECT_ALLOW_RED_ZONE": "1"}
        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-tool-use"], payload, env=env)
        self.assertEqual(rc, 0, f"Expected allow with override: {err}")
        d = json.loads(out)
        self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "allow")


class TestWaveZ32PostToolUseFailureAndPreCompact(HooksTestBase):
    """Wave Z3.2: PostToolUseFailure sliding window and PreCompact read-only advisory."""

    def test_post_tool_use_failure_circuit_breaker(self):
        session_id = "test-failure-session-1"
        payload = {"session_id": session_id, "tool_name": "edit_file"}

        # First failure: silent no-op (rc=0, {})
        rc1, out1, _ = self._run_dispatch(["--harness", "claude-code", "--event", "post-tool-use-failure"], payload)
        self.assertEqual(rc1, 0)
        d1 = json.loads(out1)
        self.assertEqual(d1, {})

        # Second failure of same tool within 5 minutes: returns hint
        rc2, out2, _ = self._run_dispatch(["--harness", "claude-code", "--event", "post-tool-use-failure"], payload)
        self.assertEqual(rc2, 0)
        d2 = json.loads(out2)
        hint = d2["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Circuit Breaker Hint", hint)
        self.assertIn("edit_file", hint)

        # Zero repository files created (all in tempfile)
        repo_files = list(self.root.rglob("meta-project-failures*"))
        self.assertEqual(len(repo_files), 0, "No failure files should be created in repository")

    def test_pre_compact_read_only_advisory(self):
        # With open PROBE in tasks.md
        tasks_content = """# Tasks
- [?] PROBE: DIAG-005 investigate memory leak
"""
        (self.pk_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

        rc, out, err = self._run_dispatch(["--harness", "claude-code", "--event", "pre-compact"], {})
        self.assertEqual(rc, 0)
        d = json.loads(out)
        ctx = d.get("hookSpecificOutput", {}).get("additionalContext") or d.get("systemMessage") or d.get("additionalContext") or ""
        self.assertIn("Pre-Compact", ctx)
        self.assertIn("DIAG-005", ctx)

        # When tasks clean
        (self.pk_dir / "tasks.md").write_text("# Tasks\n- [ ] Clean task\n", encoding="utf-8")
        rc2, out2, _ = self._run_dispatch(["--harness", "claude-code", "--event", "pre-compact"], {})
        self.assertEqual(rc2, 0)
        d2 = json.loads(out2)
        self.assertEqual(d2, {})


class TestWaveZ32ManifestAndInstaller(HooksTestBase):
    """Wave Z3.2: hooks.json quotes, 4 events, install.py lifecycle and Probe 5."""

    def _run_install(self, args: list[str]) -> tuple[int, str, str]:
        cmd = [sys.executable, str(REPO_ROOT / "hooks" / "install.py"), *args, "--repo-root", str(self.root)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr

    def test_hooks_json_has_quotes_and_all_4_events(self):
        hooks_json_path = REPO_ROOT / "hooks" / "hooks.json"
        self.assertTrue(hooks_json_path.is_file(), f"Missing {hooks_json_path}")
        content = hooks_json_path.read_text(encoding="utf-8")
        data = json.loads(content)
        hooks = data.get("hooks", {})

        # All 4 events
        self.assertIn("SessionStart", hooks)
        self.assertIn("PreToolUse", hooks)
        self.assertIn("PostToolUseFailure", hooks)
        self.assertIn("PreCompact", hooks)

        # PreToolUse has both Edit/Write and Bash
        matchers = [entry.get("matcher") for entry in hooks["PreToolUse"] if isinstance(entry, dict)]
        self.assertIn("Edit|Write|MultiEdit", matchers)
        self.assertIn("Bash", matchers)

        # Quotes around dispatch command
        self.assertIn('\\"${CLAUDE_PLUGIN_ROOT}/hooks/dispatch.py\\"', content)

    def test_install_claude_includes_bash_failure_and_compact(self):
        rc, _, err = self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        self.assertEqual(rc, 0, f"Install failed: {err}")

        settings_path = self.root / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        hooks = data["hooks"]

        self.assertIn("SessionStart", hooks)
        self.assertIn("PreToolUse", hooks)
        self.assertIn("PostToolUseFailure", hooks)
        self.assertIn("PreCompact", hooks)

        pre_matchers = [e.get("matcher") for e in hooks["PreToolUse"] if isinstance(e, dict)]
        self.assertIn("Edit|Write|MultiEdit", pre_matchers)
        self.assertIn("Bash", pre_matchers)

    def test_verify_includes_probe_5_bash(self):
        self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        rc, out, err = self._run_install(["verify", "--harness", "claude-code"])
        self.assertEqual(rc, 0, f"Verify failed: {err}")
        self.assertIn("5 live dry-run probes", out)

    def test_uninstall_cleans_all_events(self):
        self._run_install(["install", "--harness", "claude-code", "--no-git-hook"])
        rc, _, _ = self._run_install(["uninstall", "--harness", "claude-code"])
        self.assertEqual(rc, 0)

        settings_path = self.root / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertNotIn("hooks", data)


if __name__ == "__main__":
    unittest.main()
