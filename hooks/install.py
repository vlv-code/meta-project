#!/usr/bin/env python3
"""Idempotent installer, live dry-run verifier, and clean uninstaller for Meta-Project hooks.

Supports: claude-code, zcode, cursor, gemini, copilot, codex, all.
Also chains local Git pre-commit hook (check_boundaries.py) by default.

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from scripts._common import detect_host_harness
except ImportError:
    try:
        from _common import detect_host_harness
    except ImportError:
        detect_host_harness = None

DISPATCH_MARKER = "hooks/dispatch.py"
ALL_HARNESSES = ["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"]


def _get_config_path(repo_root: Path, harness: str) -> Optional[Path]:
    h = harness.strip().lower()
    if h in ("claude-code", "zcode"):
        return repo_root / ".claude" / "settings.json"
    elif h == "cursor":
        return repo_root / ".cursor" / "hooks.json"
    elif h == "gemini":
        return repo_root / ".gemini" / "settings.json"
    elif h == "copilot":
        return repo_root / ".github" / "hooks" / "meta-project.json"
    elif h == "codex":
        return repo_root / ".codex" / "hooks.json"
    return None


def _load_json_safe(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        raise ValueError(f"Root JSON is not an object: {type(data)}")
    except Exception as e:
        raise SystemExit(f"[FAIL-CLOSED] Corrupted JSON in {path}: {e}. Aborting to prevent data loss.")


def _save_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_file = path.parent / f".tmp_{path.name}_{os.getpid()}"
    try:
        temp_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        temp_file.replace(path)
    finally:
        if temp_file.exists():
            temp_file.unlink(missing_ok=True)


def _build_dispatch_command(
    harness: str,
    event: str,
    with_read_gate: bool = False,
    red_policy: str = "deny",
) -> str:
    cmd = f"python hooks/dispatch.py --harness {harness} --event {event}"
    if with_read_gate:
        cmd += " --with-read-gate"
    if red_policy != "deny":
        cmd += f" --red-policy {red_policy}"
    return cmd


def install_harness(
    repo_root: Path,
    harness: str,
    with_read_gate: bool = False,
    red_policy: str = "deny",
) -> None:
    """Install hooks for a single harness idempotently, preserving existing user hooks."""
    config_path = _get_config_path(repo_root, harness)
    if not config_path:
        return

    data = _load_json_safe(config_path)
    h = harness.strip().lower()

    if h in ("claude-code", "zcode"):
        hooks = data.setdefault("hooks", {})
        # PreToolUse
        pre = [entry for entry in hooks.get("PreToolUse", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        pre.append({"command": _build_dispatch_command(h, "pre-tool-use", with_read_gate, red_policy)})
        hooks["PreToolUse"] = pre

        # SessionStart
        start = [entry for entry in hooks.get("SessionStart", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        start.append({"command": _build_dispatch_command(h, "session-start")})
        hooks["SessionStart"] = start

        # PostToolUse if with_read_gate
        post = [entry for entry in hooks.get("PostToolUse", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        if with_read_gate:
            post.append({"command": _build_dispatch_command(h, "post-tool-use", with_read_gate=True)})
        hooks["PostToolUse"] = post

    elif h == "cursor":
        data.setdefault("version", 1)
        hooks = data.setdefault("hooks", {})
        # preToolUse with failClosed: true
        pre = [entry for entry in hooks.get("preToolUse", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        pre.append({
            "command": _build_dispatch_command(h, "pre-tool-use", with_read_gate, red_policy),
            "failClosed": True,
        })
        hooks["preToolUse"] = pre

        # sessionStart
        start = [entry for entry in hooks.get("sessionStart", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        start.append({"command": _build_dispatch_command(h, "session-start")})
        hooks["sessionStart"] = start

        # postToolUse if with_read_gate
        post = [entry for entry in hooks.get("postToolUse", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        if with_read_gate:
            post.append({"command": _build_dispatch_command(h, "post-tool-use", with_read_gate=True)})
        hooks["postToolUse"] = post

    elif h == "gemini":
        hooks = data.setdefault("hooks", {})
        # BeforeTool
        before = [entry for entry in hooks.get("BeforeTool", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        before.append({
            "matcher": "write_file|replace|replace_string|edit_file",
            "command": _build_dispatch_command(h, "pre-tool-use", with_read_gate, red_policy),
        })
        hooks["BeforeTool"] = before

        # SessionStart
        start = [entry for entry in hooks.get("SessionStart", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        start.append({
            "matcher": "startup",
            "command": _build_dispatch_command(h, "session-start"),
        })
        hooks["SessionStart"] = start

        # AfterTool if with_read_gate
        after = [entry for entry in hooks.get("AfterTool", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        if with_read_gate:
            after.append({
                "matcher": ".*",
                "command": _build_dispatch_command(h, "post-tool-use", with_read_gate=True),
            })
        hooks["AfterTool"] = after

    elif h == "copilot":
        data.setdefault("version", 1)
        hooks = data.setdefault("hooks", {})
        pre = [
            entry
            for entry in hooks.get("preToolUse", [])
            if DISPATCH_MARKER not in str(entry.get("bash", "")) and DISPATCH_MARKER not in str(entry.get("powershell", ""))
        ]
        pre.append({
            "bash": "python3 hooks/dispatch.py --harness copilot --event pre-tool-use"
            + (" --with-read-gate" if with_read_gate else "")
            + (f" --red-policy {red_policy}" if red_policy != "deny" else ""),
            "powershell": "python hooks/dispatch.py --harness copilot --event pre-tool-use"
            + (" --with-read-gate" if with_read_gate else "")
            + (f" --red-policy {red_policy}" if red_policy != "deny" else ""),
        })
        hooks["preToolUse"] = pre

        start = [
            entry
            for entry in hooks.get("sessionStart", [])
            if DISPATCH_MARKER not in str(entry.get("bash", "")) and DISPATCH_MARKER not in str(entry.get("powershell", ""))
        ]
        start.append({
            "bash": "python3 hooks/dispatch.py --harness copilot --event session-start",
            "powershell": "python hooks/dispatch.py --harness copilot --event session-start",
        })
        hooks["sessionStart"] = start

    elif h == "codex":
        hooks = data.setdefault("hooks", {})
        pre = [entry for entry in hooks.get("PreToolUse", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        pre.append({"command": _build_dispatch_command(h, "pre-tool-use", with_read_gate, red_policy)})
        hooks["PreToolUse"] = pre

        start = [entry for entry in hooks.get("SessionStart", []) if DISPATCH_MARKER not in str(entry.get("command", ""))]
        start.append({"command": _build_dispatch_command(h, "session-start")})
        hooks["SessionStart"] = start

    _save_json_atomic(config_path, data)
    print(f"[OK] Installed hooks for {harness} in {config_path}")
    if h == "codex":
        print("[NOTICE] Codex requires one-time '/hooks' approval in the interactive TUI to activate hooks.")


def uninstall_harness(repo_root: Path, harness: str) -> None:
    """Uninstall hooks for a single harness, cleanly removing only Meta-Project entries."""
    config_path = _get_config_path(repo_root, harness)
    if not config_path or not config_path.is_file():
        return

    data = _load_json_safe(config_path)
    h = harness.strip().lower()

    if h in ("claude-code", "zcode"):
        hooks = data.get("hooks", {})
        for ev in ["PreToolUse", "SessionStart", "PostToolUse"]:
            if ev in hooks:
                hooks[ev] = [e for e in hooks[ev] if DISPATCH_MARKER not in str(e.get("command", ""))]
                if not hooks[ev]:
                    del hooks[ev]
        if not hooks:
            data.pop("hooks", None)

    elif h == "cursor":
        hooks = data.get("hooks", {})
        for ev in ["preToolUse", "sessionStart", "postToolUse"]:
            if ev in hooks:
                hooks[ev] = [e for e in hooks[ev] if DISPATCH_MARKER not in str(e.get("command", ""))]
                if not hooks[ev]:
                    del hooks[ev]
        if not hooks:
            data.pop("hooks", None)

    elif h == "gemini":
        hooks = data.get("hooks", {})
        for ev in ["BeforeTool", "SessionStart", "AfterTool"]:
            if ev in hooks:
                hooks[ev] = [e for e in hooks[ev] if DISPATCH_MARKER not in str(e.get("command", ""))]
                if not hooks[ev]:
                    del hooks[ev]
        if not hooks:
            data.pop("hooks", None)

    elif h == "copilot":
        hooks = data.get("hooks", {})
        for ev in ["preToolUse", "sessionStart"]:
            if ev in hooks:
                hooks[ev] = [
                    e
                    for e in hooks[ev]
                    if DISPATCH_MARKER not in str(e.get("bash", "")) and DISPATCH_MARKER not in str(e.get("powershell", ""))
                ]
                if not hooks[ev]:
                    del hooks[ev]
        if not hooks:
            data.pop("hooks", None)

    elif h == "codex":
        hooks = data.get("hooks", {})
        for ev in ["PreToolUse", "SessionStart"]:
            if ev in hooks:
                hooks[ev] = [e for e in hooks[ev] if DISPATCH_MARKER not in str(e.get("command", ""))]
                if not hooks[ev]:
                    del hooks[ev]
        if not hooks:
            data.pop("hooks", None)

    # Special cleanup for copilot standalone file
    if h == "copilot" and not data.get("hooks"):
        config_path.unlink(missing_ok=True)
        print(f"[OK] Removed empty Copilot hook manifest: {config_path}")
        return

    _save_json_atomic(config_path, data)
    print(f"[OK] Uninstalled hooks for {harness} from {config_path}")


def verify_harness(repo_root: Path, harness: str) -> bool:
    """Verify harness hook configuration and execute 3 live dry-run probes."""
    config_path = _get_config_path(repo_root, harness)
    if not config_path or not config_path.is_file():
        print(f"[FAIL] Config file not found for {harness}: {config_path}")
        return False

    try:
        text = config_path.read_text(encoding="utf-8")
        if DISPATCH_MARKER not in text:
            print(f"[FAIL] Marker '{DISPATCH_MARKER}' absent from {config_path}")
            return False
        json.loads(text)
    except Exception as e:
        print(f"[FAIL] Syntax error in {config_path}: {e}")
        return False

    h = harness.strip().lower()

    # Determine configured red_policy from config text
    red_policy = "ask" if "--red-policy ask" in text else "deny"

    dispatch_script = repo_root / "hooks" / "dispatch.py"
    if not dispatch_script.is_file():
        # Fallback to current repo root if running from checkout
        dispatch_script = Path(__file__).resolve().parent / "dispatch.py"

    # Probe 1: session-start (rc=0, valid JSON, <= 4000 chars)
    cmd1 = [sys.executable, str(dispatch_script), "--harness", h, "--event", "session-start"]
    proc1 = subprocess.run(cmd1, input="{}", capture_output=True, text=True, cwd=str(repo_root))
    if proc1.returncode != 0:
        print(f"[FAIL] Probe 1 (session-start) failed (rc={proc1.returncode}): {proc1.stderr}")
        return False
    try:
        d1 = json.loads(proc1.stdout)
        ctx = (
            d1.get("hookSpecificOutput", {}).get("additionalContext")
            or d1.get("systemMessage")
            or d1.get("additionalContext")
            or ""
        )
        if len(ctx) > 4000:
            print(f"[FAIL] Probe 1 context exceeded 4000 chars ({len(ctx)})")
            return False
    except Exception as e:
        print(f"[FAIL] Probe 1 output is not valid JSON: {e}")
        return False

    # Probe 2: pre-tool-use on Green path (rc=0, allow)
    cmd2 = [sys.executable, str(dispatch_script), "--harness", h, "--event", "pre-tool-use"]
    payload_green = json.dumps({"tool_name": "write_file", "tool_input": {"path": "README.md"}})
    proc2 = subprocess.run(cmd2, input=payload_green, capture_output=True, text=True, cwd=str(repo_root))
    if proc2.returncode != 0:
        print(f"[FAIL] Probe 2 (Green path allow) failed (rc={proc2.returncode}): {proc2.stderr}")
        return False
    try:
        d2 = json.loads(proc2.stdout)
        decision = (
            d2.get("hookSpecificOutput", {}).get("permissionDecision")
            or d2.get("permission")
            or d2.get("permissionDecision")
            or d2.get("decision")
        )
        if decision != "allow":
            print(f"[FAIL] Probe 2 expected allow, got {decision}")
            return False
    except Exception as e:
        print(f"[FAIL] Probe 2 output is not valid JSON: {e}")
        return False

    # Probe 3: pre-tool-use on Red path (deny or ask)
    cmd3 = [sys.executable, str(dispatch_script), "--harness", h, "--event", "pre-tool-use"]
    if red_policy == "ask":
        cmd3.extend(["--red-policy", "ask"])
    payload_red = json.dumps({"tool_name": "write_file", "tool_input": {"path": "scripts/check_boundaries.py"}})
    proc3 = subprocess.run(cmd3, input=payload_red, capture_output=True, text=True, cwd=str(repo_root))

    if h == "gemini":
        expected_rc = 0
    elif red_policy == "ask" and h in ("claude-code", "zcode"):
        expected_rc = 0
    else:
        expected_rc = 2

    if proc3.returncode != expected_rc:
        print(f"[FAIL] Probe 3 expected rc={expected_rc}, got {proc3.returncode}")
        return False

    try:
        d3 = json.loads(proc3.stdout)
        decision3 = (
            d3.get("hookSpecificOutput", {}).get("permissionDecision")
            or d3.get("permission")
            or d3.get("permissionDecision")
            or d3.get("decision")
        )
        expected_decision = "ask" if (red_policy == "ask" and h in ("claude-code", "zcode", "gemini")) else ("block" if h == "codex" else "deny")
        if decision3 != expected_decision:
            print(f"[FAIL] Probe 3 expected {expected_decision}, got {decision3}")
            return False
    except Exception as e:
        print(f"[FAIL] Probe 3 output is not valid JSON: {e}")
        return False

    print(f"[OK] Harness {harness} passed syntax, marker, and 3 live dry-run probes.")
    if h == "zcode":
        print("[ZCODE-VERIFIED] ZCode live-session hooks verified: settings.json PreToolUse and SessionStart pass live dry-run probes.")
    return True


def _install_git_precommit(repo_root: Path) -> None:
    """Install or chain Git pre-commit hook via check_boundaries.py."""
    git_dir = repo_root / ".git"
    if not git_dir.is_dir():
        return

    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    framework_root = Path(__file__).resolve().parent.parent
    if str(framework_root / "scripts") not in sys.path:
        sys.path.insert(0, str(framework_root / "scripts"))

    try:
        try:
            from scripts import check_boundaries
        except ImportError:
            import check_boundaries

        if hasattr(check_boundaries, "install_git_hook"):
            check_boundaries.install_git_hook(repo_root)
            print("[OK] Installed Git pre-commit hook via check_boundaries.")
        else:
            cmd = [sys.executable, str(repo_root / "scripts" / "check_boundaries.py"), "--install-hook"]
            subprocess.run(cmd, check=True, cwd=str(repo_root))
            print("[OK] Installed Git pre-commit hook via check_boundaries CLI.")
    except Exception as e:
        print(f"[WARN] Could not install Git pre-commit hook: {e}")


def _uninstall_git_precommit(repo_root: Path) -> None:
    hook_file = repo_root / ".git" / "hooks" / "pre-commit"
    if hook_file.is_file():
        try:
            text = hook_file.read_text(encoding="utf-8")
            if "check_boundaries" in text:
                hook_file.unlink()
                print("[OK] Removed Git pre-commit hook.")
        except Exception as e:
            print(f"[WARN] Failed to remove Git pre-commit hook: {e}")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Meta-Project hook installation and management utility")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # install
    p_install = subparsers.add_parser("install", help="Install harness hook configuration")
    p_install.add_argument("--harness", required=True, choices=[*ALL_HARNESSES, "all"])
    p_install.add_argument("--repo-root", default=".", help="Target repository root (default: .)")
    p_install.add_argument("--with-read-gate", action="store_true", help="Enable opt-in read journal gate")
    p_install.add_argument("--red-policy", choices=["deny", "ask"], default="deny", help="Red-zone policy (default: deny)")
    p_install.add_argument("--no-git-hook", action="store_true", help="Do not install Git pre-commit hook")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify harness hook configuration and run live dry-run probes")
    p_verify.add_argument("--harness", required=True, choices=[*ALL_HARNESSES, "all"])
    p_verify.add_argument("--repo-root", default=".", help="Target repository root (default: .)")

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Uninstall harness hook configuration")
    p_uninstall.add_argument("--harness", required=True, choices=[*ALL_HARNESSES, "all"])
    p_uninstall.add_argument("--repo-root", default=".", help="Target repository root (default: .)")
    p_uninstall.add_argument("--with-git-hook", action="store_true", help="Also remove Git pre-commit hook")

    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    target_harnesses = ALL_HARNESSES if args.harness == "all" else [args.harness]

    if args.subcommand == "install":
        for h in target_harnesses:
            install_harness(repo_root, h, args.with_read_gate, args.red_policy)
        if not args.no_git_hook:
            _install_git_precommit(repo_root)

    elif args.subcommand == "verify":
        all_ok = True
        for h in target_harnesses:
            if not verify_harness(repo_root, h):
                all_ok = False
        if not all_ok:
            sys.exit(1)

    elif args.subcommand == "uninstall":
        for h in target_harnesses:
            uninstall_harness(repo_root, h)
        if args.with_git_hook:
            _uninstall_git_precommit(repo_root)


if __name__ == "__main__":
    main()
