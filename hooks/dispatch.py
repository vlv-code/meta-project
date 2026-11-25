#!/usr/bin/env python3
"""Unified stdlib event dispatcher for Meta-Project thin hooks layer.

Supported harnesses: claude-code, zcode, cursor, gemini, copilot, codex.
Supported events: pre-tool-use, post-tool-use, session-start.

Zero-dependency: Python 3.10+ stdlib only.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from scripts._common import detect_host_harness
except ImportError:
    try:
        from _common import detect_host_harness
    except ImportError:
        detect_host_harness = None


def _find_repo_root(cwd_hint: Optional[Path] = None) -> Optional[Path]:
    """Find meta-project repository root by searching upward for boundaries.md."""
    curr = (cwd_hint or Path.cwd()).resolve()
    for _ in range(64):
        if (curr / ".agents" / "project_knowledge" / "boundaries.md").is_file():
            return curr
        if curr.parent == curr:
            break
        curr = curr.parent
    return None


def _extract_paths_from_payload(payload: Dict[str, Any]) -> List[str]:
    """Extract candidate target file paths from hook payload."""
    tool_name = str(payload.get("tool_name", "")).strip()
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except Exception:
            tool_input = {"input": tool_input}
    if not isinstance(tool_input, dict):
        return []

    extracted: List[str] = []

    # Check for Codex apply_patch or patch input
    patch_text = ""
    if tool_name == "apply_patch" or "patch" in tool_input or "input" in tool_input:
        patch_text = str(tool_input.get("patch") or tool_input.get("input") or "")
        if patch_text:
            for line in patch_text.splitlines():
                line_s = line.strip()
                m = re.match(r"^\*\*\*\s*(?:Update|Add|Delete)\s*File:\s*(.+)$", line_s, re.IGNORECASE)
                if m:
                    extracted.append(m.group(1).strip())

    # Candidate path keys
    candidate_keys = [
        "file_path",
        "path",
        "TargetFile",
        "target_file",
        "AbsolutePath",
        "Path",
        "file",
    ]
    for key in candidate_keys:
        if key in tool_input and tool_input[key]:
            val = str(tool_input[key]).strip()
            if val and val not in extracted:
                extracted.append(val)

    return extracted


def _emit_response(
    harness: str,
    event: str,
    decision: str,
    reason: str = "",
    context: str = "",
) -> None:
    """Format and print the exact JSON response for the target harness on stdout."""
    harness_norm = harness.strip().lower()
    event_norm = event.strip().lower()
    res: Dict[str, Any] = {}

    if event_norm == "session-start":
        if harness_norm in ("claude-code", "zcode"):
            res = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        elif harness_norm == "gemini":
            res = {"systemMessage": context}
        else:
            # cursor, copilot, codex
            res = {"additionalContext": context}

    elif event_norm in ("post-tool-use-failure", "pre-compact"):
        if not context:
            res = {}
        elif harness_norm in ("claude-code", "zcode"):
            res = {
                "hookSpecificOutput": {
                    "hookEventName": (
                        "PostToolUseFailure" if event_norm == "post-tool-use-failure" else "PreCompact"
                    ),
                    "additionalContext": context,
                }
            }
        elif harness_norm == "gemini":
            res = {"systemMessage": context}
        else:
            res = {"additionalContext": context}

    elif event_norm == "post-tool-use":
        res = {}

    else:  # pre-tool-use
        if harness_norm in ("claude-code", "zcode"):
            output: Dict[str, Any] = {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
            }
            if decision in ("deny", "ask") and reason:
                output["permissionDecisionReason"] = reason
            res = {"hookSpecificOutput": output}

        elif harness_norm == "gemini":
            if decision == "allow":
                res = {"decision": "allow"}
            elif decision == "ask":
                res = {"decision": "ask", "reason": reason, "systemMessage": reason}
            else:
                res = {"decision": "deny", "reason": reason, "systemMessage": reason}

        elif harness_norm == "cursor":
            if decision == "allow":
                res = {"permission": "allow"}
            else:
                res = {"permission": "deny", "user_message": reason, "agent_message": reason}

        elif harness_norm == "copilot":
            if decision == "allow":
                res = {"permissionDecision": "allow"}
            else:
                res = {"permissionDecision": "deny", "permissionDecisionReason": reason}

        elif harness_norm == "codex":
            if decision == "allow":
                res = {"decision": "allow"}
            else:
                res = {"decision": "block", "reason": reason}

    # Strict stdout purity: print ONLY JSON
    sys.stdout.write(json.dumps(res))
    sys.stdout.flush()


def _handle_session_start(
    repo_root: Optional[Path],
    harness: str,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Handle session-start event with read-only context gathering (budget <= 4000)."""
    if repo_root is None:
        _emit_response(harness, "session-start", decision="allow", context="")
        sys.exit(0)

    # Ensure scripts directory and framework root are in sys.path
    framework_root = Path(__file__).resolve().parent.parent
    for p_dir in [repo_root, repo_root / "scripts", framework_root, framework_root / "scripts"]:
        if str(p_dir) not in sys.path:
            sys.path.insert(0, str(p_dir))

    context_parts: List[str] = []

    # 1. State and facts_digest via inspect_meta_project
    try:
        try:
            from scripts import inspect_meta_project
        except ImportError:
            import inspect_meta_project

        target_harness = harness
        if detect_host_harness:
            detected = detect_host_harness()
            if detected:
                if harness in ("claude-code", "zcode") and detected == "zcode":
                    target_harness = "zcode"
                elif detected != "antigravity":
                    target_harness = detected

        with contextlib.redirect_stdout(io.StringIO()):
            report = inspect_meta_project.inspect_repository(repo_root, target_harness=target_harness)
            digest = inspect_meta_project.compute_facts_digest(repo_root, report)

        state = report.get("state", "UNKNOWN")
        proj_id = report.get("project_id", "unregistered")
        inst_id = (
            report.get("runtime_context", {}).get("target_installation")
            or report.get("resolved_target_installation")
            or report.get("installation_id")
            or "unbound"
        )
        context_parts.append(f"Meta-Project Environment: State={state} | Project={proj_id} | Installation={inst_id}")

        # Active slices
        slices = [s for s, h in digest.get("slices", {}).items() if h is not None]
        context_parts.append(f"Active Knowledge Slices: {', '.join(slices) if slices else 'none'}")
    except Exception:
        context_parts.append(f"Meta-Project Environment: active at {repo_root.name}")

    # 2. Epistemic check: open hypotheses/probes from tasks.md via triage_incident
    tasks_file = repo_root / ".agents" / "project_knowledge" / "tasks.md"
    if tasks_file.is_file():
        try:
            try:
                from scripts import triage_incident
            except ImportError:
                import triage_incident

            tasks_text = tasks_file.read_text(encoding="utf-8")
            blocks = triage_incident._parse_task_blocks(tasks_text)
            open_items: List[str] = []
            for b in blocks:
                diag = triage_incident._analyze_diagnostic_block(b)
                if diag and not diag.get("verified"):
                    open_items.append(diag.get("explicit_id") or diag.get("header") or diag.get("id"))
                elif b.get("status_char") in ("?", " ") and any(
                    k in b.get("header", "").lower() for k in ("hypothesis", "probe", "diag-", "unverified")
                ):
                    open_items.append(b.get("header", "")[:80])
            if open_items:
                context_parts.append(
                    f"Epistemic Alert: {len(open_items)} open unverified item(s) in tasks.md: "
                    + "; ".join(open_items[:3])
                )
        except Exception:
            pass

    # 3. Compact memory advisory via compact_memory in-memory dry-run
    obs_file = repo_root / ".agents" / "project_knowledge" / "observations.md"
    needs_compact: List[str] = []
    if obs_file.is_file():
        try:
            try:
                from scripts import compact_memory
            except ImportError:
                import compact_memory

            obs_text = obs_file.read_text(encoding="utf-8")
            c_obs, _, _ = compact_memory.compact_observations(obs_text)
            if c_obs:
                needs_compact.append("observations.md")
        except Exception:
            pass

    if tasks_file.is_file():
        try:
            try:
                from scripts import compact_memory
            except ImportError:
                import compact_memory

            tasks_text = tasks_file.read_text(encoding="utf-8")
            c_tasks, _, _ = compact_memory.compact_tasks(tasks_text)
            if c_tasks:
                needs_compact.append("tasks.md")
        except Exception:
            pass

    if needs_compact:
        context_parts.append(
            f"Memory Advisory: {', '.join(needs_compact)} recommend running scripts/compact_memory.py --dry-run."
        )

    # 4. Post-compaction grounding
    if isinstance(payload, dict) and (payload.get("source") == "compact" or payload.get("trigger") == "compact"):
        context_parts.append(
            "Post-Compaction Grounding:\n"
            "Distinguish verified FACTS vs HYPOTHESES (unverified assumptions). "
            "Re-read AGENTS.md and active knowledge slices before acting on assumptions."
        )

    rendered = "\n".join(context_parts)
    # Hard budget: <= 4000 characters
    if len(rendered) > 4000:
        rendered = rendered[:3997] + "..."

    _emit_response(harness, "session-start", decision="allow", context=rendered)
    sys.exit(0)


def _handle_post_tool_use(
    repo_root: Optional[Path],
    harness: str,
    payload: Dict[str, Any],
    with_read_gate: bool,
) -> None:
    """Handle post-tool-use event: record read files in temp journal if --with-read-gate."""
    if not with_read_gate or repo_root is None:
        _emit_response(harness, "post-tool-use", decision="allow")
        sys.exit(0)

    session_id = payload.get("session_id")
    if not session_id:
        _emit_response(harness, "post-tool-use", decision="allow")
        sys.exit(0)

    tool_name = str(payload.get("tool_name", "")).strip().lower()
    if tool_name in READ_TOOLS:
        paths = _extract_paths_from_payload(payload)
        if paths:
            target_path = paths[0]
            try:
                p = Path(target_path)
                if p.is_absolute():
                    rel = p.resolve().relative_to(repo_root.resolve()).as_posix()
                else:
                    rel = p.as_posix()
                if rel.startswith("./"):
                    rel = rel[2:]

                token = hashlib.sha256((str(repo_root.resolve()) + ":" + str(session_id)).encode("utf-8")).hexdigest()[:16]
                journal_path = Path(tempfile.gettempdir()) / f"meta-project-reads-{token}.txt"

                existing: List[str] = []
                if journal_path.is_file():
                    existing = [
                        line.strip()
                        for line in journal_path.read_text(encoding="utf-8").splitlines()
                        if line.strip()
                    ]
                if rel not in existing and len(existing) < 512:
                    existing.append(rel)
                    journal_path.write_text("\n".join(existing) + "\n", encoding="utf-8")
            except Exception:
                pass

    _emit_response(harness, "post-tool-use", decision="allow")
    sys.exit(0)


READ_TOOLS = {
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
}


def _handle_pre_tool_use(
    repo_root: Optional[Path],
    harness: str,
    payload: Dict[str, Any],
    with_read_gate: bool,
    red_policy: str,
) -> None:
    """Handle pre-tool-use event: boundary gate + optional read-journal gate."""
    if repo_root is None:
        _emit_response(harness, "pre-tool-use", decision="allow")
        sys.exit(0)

    tool_name = str(payload.get("tool_name", "")).strip().lower()

    # ADR #15 (Read Permissions vs Write Restrictions):
    # Read-only and non-mutating inspection tools are NEVER restricted by boundary gates,
    # even when targeting Red Zone files (boundaries.md, check_boundaries.py, test_integrity.py).
    # This guarantees that agents can freely read boundaries and weak spots without deadlocking.
    if tool_name in READ_TOOLS:
        _emit_response(harness, "pre-tool-use", decision="allow", reason="Read-only operation allowed (ADR #15)")
        sys.exit(0)

    # Wave Z3.2: Narrow anti-bypass Bash guard
    if tool_name in ("bash", "shell", "run_command", "execute_command", "terminal"):
        tool_input = payload.get("tool_input", {})
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except Exception:
                tool_input = {"command": tool_input}
        cmd_str = ""
        if isinstance(tool_input, dict):
            cmd_str = str(
                tool_input.get("command")
                or tool_input.get("CommandLine")
                or tool_input.get("cmd")
                or ""
            ).strip()
        elif isinstance(tool_input, str):
            cmd_str = tool_input.strip()

        # Check override
        if os.environ.get("META_PROJECT_ALLOW_RED_ZONE") == "1":
            _emit_response(
                harness,
                "pre-tool-use",
                decision="allow",
                reason="Override active (META_PROJECT_ALLOW_RED_ZONE=1)",
            )
            sys.exit(0)

        # Deny git commit with --no-verify or -n
        # Deny git push with --force, -f, or --force-with-lease
        deny_reason: Optional[str] = None
        if re.search(r"\bgit\s+commit\b.*(?:\s--no-verify\b|\s-n\b)", cmd_str):
            deny_reason = "Bypassing pre-commit checks with 'git commit --no-verify' is denied by Meta-Project policy"
        elif re.search(r"\bgit\s+push\b.*(?:\s--force\b|\s-f\b|\s--force-with-lease\b)", cmd_str):
            deny_reason = "Force-pushing with 'git push --force' is denied by Meta-Project policy"

        if deny_reason:
            _emit_response(harness, "pre-tool-use", decision="deny", reason=deny_reason)
            sys.exit(0 if harness == "gemini" else 2)

        _emit_response(harness, "pre-tool-use", decision="allow", reason="Safe shell command allowed")
        sys.exit(0)

    raw_paths = _extract_paths_from_payload(payload)
    if not raw_paths:
        # Non-file tool (e.g. bash, search, status) -> allow
        _emit_response(harness, "pre-tool-use", decision="allow")
        sys.exit(0)

    # Normalize paths relative to repo_root
    rel_paths: List[str] = []
    repo_root_res = repo_root.resolve()
    for raw in raw_paths:
        p = Path(raw)
        if p.is_absolute():
            try:
                rel = p.resolve().relative_to(repo_root_res).as_posix()
                rel_paths.append(rel)
            except ValueError:
                # File outside repository root -> do not govern
                continue
        else:
            norm = p.as_posix()
            if norm.startswith("./"):
                norm = norm[2:]
            rel_paths.append(norm)

    if not rel_paths:
        # All target files were outside repo root -> allow
        _emit_response(harness, "pre-tool-use", decision="allow")
        sys.exit(0)

    # Load and parse boundaries.md
    boundaries_file = repo_root / ".agents" / "project_knowledge" / "boundaries.md"
    if not boundaries_file.is_file():
        # boundaries.md was unexpectedly missing inside repo -> fail closed
        _emit_response(harness, "pre-tool-use", decision="deny", reason="boundaries.md is missing or unreadable")
        sys.exit(0 if harness == "gemini" else 2)

    try:
        boundaries_content = boundaries_file.read_text(encoding="utf-8")
        if not boundaries_content.strip():
            raise ValueError("boundaries.md is empty")
    except Exception as e:
        _emit_response(harness, "pre-tool-use", decision="deny", reason=f"Failed to read boundaries.md: {e}")
        sys.exit(0 if harness == "gemini" else 2)

    # Ensure repo_root, repo_root/scripts, and framework root are in sys.path
    framework_root = Path(__file__).resolve().parent.parent
    for p_dir in [repo_root, repo_root / "scripts", framework_root, framework_root / "scripts"]:
        if str(p_dir) not in sys.path:
            sys.path.insert(0, str(p_dir))

    try:
        try:
            from scripts import check_boundaries
        except ImportError:
            import check_boundaries

        zones = check_boundaries.parse_boundaries(boundaries_content)
    except Exception as e:
        _emit_response(harness, "pre-tool-use", decision="deny", reason=f"Failed to parse boundaries.md: {e}")
        sys.exit(0 if harness == "gemini" else 2)

    # Classify all extracted paths. Most restrictive zone wins: black/red > yellow > green
    zone_priority = {"black": 4, "red": 3, "yellow": 2, "green": 1}
    most_restrictive_zone = "green"
    most_restrictive_reason = "Green Zone (Unrestricted)"
    most_restrictive_path = rel_paths[0]
    highest_prio = 0

    for rpath in rel_paths:
        z, r = check_boundaries.classify_path(rpath, zones)
        prio = zone_priority.get(z, 4)
        if prio > highest_prio:
            highest_prio = prio
            most_restrictive_zone = z
            most_restrictive_reason = r
            most_restrictive_path = rpath

    # Evaluate decision matrix
    if most_restrictive_zone in ("red", "black"):
        # 1. Environment override
        if os.environ.get("META_PROJECT_ALLOW_RED_ZONE") == "1":
            _emit_response(
                harness,
                "pre-tool-use",
                decision="allow",
                reason=f"Override active (META_PROJECT_ALLOW_RED_ZONE=1) for {most_restrictive_path}",
            )
            sys.exit(0)

        # 2. Interactive ask policy on supported harnesses
        if red_policy == "ask" and harness in ("claude-code", "zcode", "gemini"):
            _emit_response(
                harness,
                "pre-tool-use",
                decision="ask",
                reason=f"Target file '{most_restrictive_path}' is in {most_restrictive_zone.title()} Zone ({most_restrictive_reason}). Confirm modification.",
            )
            sys.exit(0)

        # 3. Fail-closed deny
        _emit_response(
            harness,
            "pre-tool-use",
            decision="deny",
            reason=f"Target file '{most_restrictive_path}' is in {most_restrictive_zone.title()} Zone ({most_restrictive_reason}). Modification denied.",
        )
        sys.exit(0 if harness == "gemini" else 2)

    elif most_restrictive_zone == "yellow":
        if with_read_gate:
            session_id = payload.get("session_id")
            if session_id:
                token = hashlib.sha256((str(repo_root_res) + ":" + str(session_id)).encode("utf-8")).hexdigest()[:16]
                journal_path = Path(tempfile.gettempdir()) / f"meta-project-reads-{token}.txt"
                read_files: set[str] = set()
                if journal_path.is_file():
                    try:
                        read_files = {
                            line.strip()
                            for line in journal_path.read_text(encoding="utf-8").splitlines()
                            if line.strip()
                        }
                    except Exception:
                        pass

                # Require boundaries.md
                has_read_boundaries = any("boundaries.md" in rf for rf in read_files)
                if not has_read_boundaries:
                    _emit_response(
                        harness,
                        "pre-tool-use",
                        decision="deny",
                        reason="Modifying Yellow Zone files requires reading .agents/project_knowledge/boundaries.md first (--with-read-gate)",
                    )
                    sys.exit(0 if harness == "gemini" else 2)

                # Require weak_spots.md if relevant
                weak_spots_file = repo_root / ".agents" / "project_knowledge" / "weak_spots.md"
                if weak_spots_file.is_file():
                    try:
                        ws_text = weak_spots_file.read_text(encoding="utf-8")
                        target_name = Path(most_restrictive_path).name
                        target_stem = Path(most_restrictive_path).stem
                        if target_name in ws_text or target_stem in ws_text or most_restrictive_path in ws_text:
                            has_read_weak_spots = any("weak_spots.md" in rf for rf in read_files)
                            if not has_read_weak_spots:
                                _emit_response(
                                    harness,
                                    "pre-tool-use",
                                    decision="deny",
                                    reason=f"Target '{most_restrictive_path}' is referenced in weak_spots.md; reading .agents/project_knowledge/weak_spots.md is required first (--with-read-gate)",
                                )
                                sys.exit(0 if harness == "gemini" else 2)
                    except Exception:
                        pass

        _emit_response(harness, "pre-tool-use", decision="allow", reason=most_restrictive_reason)
        sys.exit(0)

    else:
        # Green Zone
        _emit_response(harness, "pre-tool-use", decision="allow", reason=most_restrictive_reason)
        sys.exit(0)


def _handle_post_tool_use_failure(
    repo_root: Optional[Path],
    harness: str,
    payload: Dict[str, Any],
) -> None:
    """Handle post-tool-use-failure with sliding window circuit breaker in tempdir."""
    session_id = payload.get("session_id") or "default-session"
    tool_name = str(payload.get("tool_name", "")).strip().lower() or "unknown-tool"

    repo_token = (
        hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:12]
        if repo_root is not None
        else "norepo"
    )
    token = hashlib.sha256(f"{repo_token}:{session_id}".encode("utf-8")).hexdigest()[:16]
    journal_path = Path(tempfile.gettempdir()) / f"meta-project-failures-{token}.json"

    now = time.time()
    failures: List[Dict[str, Any]] = []

    if journal_path.is_file():
        try:
            raw = json.loads(journal_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                # Retain failures within 5-minute sliding window (300s), max 64 items
                failures = [
                    f for f in raw
                    if isinstance(f, dict) and now - f.get("ts", 0) < 300
                ][-63:]
        except Exception:
            failures = []

    failures.append({"tool": tool_name, "ts": now})
    try:
        journal_path.write_text(json.dumps(failures), encoding="utf-8")
    except Exception:
        pass

    # Count failures of the same tool in the current window
    same_tool_failures = sum(1 for f in failures if f.get("tool") == tool_name)
    if same_tool_failures >= 2:
        hint = (
            f"[Circuit Breaker Hint] Repeated tool failure ({same_tool_failures}x) detected for '{tool_name}'. "
            "Per Meta-Project North Stars: STOP iterative blind fixes, inspect error traces, "
            "verify assumptions against boundaries/weak_spots, and consider triage-incident before retrying."
        )
        _emit_response(harness, "post-tool-use-failure", decision="allow", context=hint)
    else:
        _emit_response(harness, "post-tool-use-failure", decision="allow", context="")
    sys.exit(0)


def _handle_pre_compact(
    repo_root: Optional[Path],
    harness: str,
    payload: Dict[str, Any],
) -> None:
    """Handle pre-compact read-only advisory."""
    if repo_root is None:
        _emit_response(harness, "pre-compact", decision="allow", context="")
        sys.exit(0)

    # Ensure scripts directory and framework root are in sys.path
    framework_root = Path(__file__).resolve().parent.parent
    p_dirs = [framework_root, framework_root / "scripts"]
    if repo_root is not None:
        p_dirs.extend([repo_root, repo_root / "scripts"])
    for p_dir in p_dirs:
        if str(p_dir) not in sys.path:
            sys.path.insert(0, str(p_dir))

    advisories: List[str] = []

    # Check open probes in tasks.md via triage_incident
    tasks_file = repo_root / ".agents" / "project_knowledge" / "tasks.md"
    if tasks_file.is_file():
        try:
            try:
                from scripts import triage_incident
            except ImportError:
                import triage_incident

            tasks_text = tasks_file.read_text(encoding="utf-8")
            blocks = triage_incident._parse_task_blocks(tasks_text)
            open_items: List[str] = []
            for b in blocks:
                diag = triage_incident._analyze_diagnostic_block(b)
                if diag and not diag.get("verified"):
                    open_items.append(diag.get("explicit_id") or diag.get("header") or diag.get("id"))
                elif b.get("status_char") in ("?", " ") and any(
                    k in b.get("header", "").lower() for k in ("hypothesis", "probe", "diag-")
                ):
                    open_items.append(b.get("header", "")[:80])
            if open_items:
                advisories.append(
                    f"Pre-Compact Epistemic Advisory: {len(open_items)} unverified diagnostic item(s) pending: "
                    + "; ".join(open_items[:3])
                )
        except Exception:
            pass

    # Check compaction status
    obs_file = repo_root / ".agents" / "project_knowledge" / "observations.md"
    if obs_file.is_file() and tasks_file.is_file():
        try:
            try:
                from scripts import compact_memory
            except ImportError:
                import compact_memory

            obs_text = obs_file.read_text(encoding="utf-8")
            tasks_text = tasks_file.read_text(encoding="utf-8")
            c_obs, _, _ = compact_memory.compact_observations(obs_text)
            c_tasks, _, _ = compact_memory.compact_tasks(tasks_text)
            if c_obs or c_tasks:
                advisories.append("Pre-Compact Memory Advisory: Memory tables ready for compaction.")
        except Exception:
            pass

    if advisories:
        msg = "\n".join(advisories)
        _emit_response(harness, "pre-compact", decision="allow", context=msg)
    else:
        _emit_response(harness, "pre-compact", decision="allow", context="")
    sys.exit(0)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Meta-Project thin hooks event dispatcher")
    parser.add_argument(
        "--harness",
        required=True,
        choices=["claude-code", "zcode", "cursor", "gemini", "copilot", "codex"],
        help="Target coding agent harness",
    )
    parser.add_argument(
        "--event",
        required=True,
        choices=[
            "pre-tool-use",
            "post-tool-use",
            "session-start",
            "post-tool-use-failure",
            "pre-compact",
        ],
        help="Hook event to handle",
    )
    parser.add_argument(
        "--with-read-gate",
        action="store_true",
        help="Enforce reading boundaries/weak_spots prior to Yellow Zone modifications",
    )
    parser.add_argument(
        "--red-policy",
        choices=["deny", "ask"],
        default="deny",
        help="Policy for Red Zone actions (default: deny)",
    )
    args = parser.parse_args(argv)

    # Read stdin payload
    raw_stdin = sys.stdin.read()
    payload: Dict[str, Any] = {}
    if raw_stdin.strip():
        try:
            payload = json.loads(raw_stdin)
        except Exception:
            # If JSON is malformed and repo has boundaries -> fail closed
            cwd_hint = Path.cwd()
            repo_root = _find_repo_root(cwd_hint)
            if repo_root is not None:
                _emit_response(args.harness, args.event, decision="deny", reason="Malformed JSON payload on stdin")
                sys.exit(0 if args.harness == "gemini" else 2)
            else:
                _emit_response(args.harness, args.event, decision="allow", reason="")
                sys.exit(0)

    # Resolve repo root
    cwd_hint = None
    if isinstance(payload, dict) and payload.get("cwd"):
        cwd_hint = Path(str(payload["cwd"]))
    repo_root = _find_repo_root(cwd_hint)

    if args.event == "session-start":
        _handle_session_start(repo_root, args.harness, payload)
    elif args.event == "post-tool-use":
        _handle_post_tool_use(repo_root, args.harness, payload, args.with_read_gate)
    elif args.event == "pre-tool-use":
        _handle_pre_tool_use(repo_root, args.harness, payload, args.with_read_gate, args.red_policy)
    elif args.event == "post-tool-use-failure":
        _handle_post_tool_use_failure(repo_root, args.harness, payload)
    elif args.event == "pre-compact":
        _handle_pre_compact(repo_root, args.harness, payload)


if __name__ == "__main__":
    main()
