#!/usr/bin/env python3
"""
Epistemic Incident Triage & Evidence Gate CLI Utility (Wave K, roadmap §10).
Zero-dependency utility (pure Python 3.10+ standard library).

Enforces evidence-first triage mechanics in tasks.md and artifact inspection:
  - probe           : log/update `- [?] PROBE` + fail-closed Circuit Breaker on >= 2
                      hypothesis revisions without new empirical evidence
  - record-evidence : atomically attach verified `evidence:` + optional artifact hash
  - promote         : fail-closed gate requiring recorded `evidence:` before
                      promoting `- [?] PROBE` to `- [ ] FIX` and emitting a Handoff Packet
  - check-tasks     : deterministic classification into verified_facts,
                      unverified_hypotheses, and thrashing_ids
  - artifact        : exact size_bytes, sha256, mtime_utc and IDENTICAL_BYTES/DIFFERS compare
"""

from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Union

try:  # shared helpers (ADR #22): package-style import
    from scripts._common import _error_envelope, _utc_now_iso
except ImportError:  # direct script execution: python scripts/triage_incident.py
    from _common import _error_envelope, _utc_now_iso

DEFAULT_TASKS_HEADER = (
    "# Current and Active Project Tasks\n\n"
    "## Execution Plan and Checklist\n\n"
)

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")
_SAFE_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,127}$")
_TOP_TASK_RE = re.compile(r"^-\s+\[([? xX>])\]\s+(.*)$")
_PROBE_OR_FIX_RE = re.compile(
    r"^(PROBE|FIX)\s+\[([^\]]+)\]\s+([A-Za-z0-9][A-Za-z0-9._:-]*)\b(?::\s*(.*))?$"
)
_LEADING_PROBE_FIX_TEXT_RE = re.compile(
    r"^(?:\[[^\]]+\]\s+)?(PROBE|FIX)(?:\s|:|$)"
)
_INCIDENT_ID_RE = re.compile(r"\b((?:DIAG|INC)-[A-Za-z0-9._-]+)\b")
_CLAIM_MARKER_RE = re.compile(
    r"(?i)(?:\b(?:root[\s_]cause|proven)\b|(?<!\w)финал(?:ьн\w*)?(?!\w))"
)
_REVISIONS_SUB_RE = re.compile(r"^\s+-\s+revisions:\s*(\d+)\s*$")
_HYPOTHESIS_SUB_RE = re.compile(r"^\s+-\s+hypothesis(?:\s*\[\d+\])?:\s*(.+)$")
_EVIDENCE_SUB_RE = re.compile(r"^\s+-\s+evidence(?:\s*\[[^\]]*\])?:\s*(.+)$")
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")

_PLACEHOLDER_VALUES = frozenset({
    "",
    "tbd",
    "todo",
    "none",
    "n/a",
    "na",
    "null",
    "pending",
    "...",
    "-",
    "?",
})


class TriageError(Exception):
    """Fail-closed domain/security error carrying an ADR envelope code."""

    def __init__(
        self,
        code: str,
        file_ref: str,
        reason: str,
        expected: str,
        actual: str,
        next_step: str,
    ) -> None:
        super().__init__(reason)
        self.code = code
        self.file_ref = file_ref
        self.reason = reason
        self.expected = expected
        self.actual = actual
        self.next_step = next_step


def _unlink_lock_file(path: Path) -> None:
    """Best-effort cleanup of advisory lock file after release."""
    for attempt in range(2):
        try:
            path.unlink()
            return
        except FileNotFoundError:
            return
        except OSError:
            if attempt == 0:
                time.sleep(0.05)


@contextlib.contextmanager
def file_lock(
    target: Union[str, os.PathLike[str], Any],
    blocking: bool = True,
    cleanup: bool = True,
):
    """Cross-platform advisory file lock (Windows msvcrt / POSIX fcntl)."""
    opened_here = False
    owned_path: Optional[Path] = None
    if isinstance(target, (str, os.PathLike)):
        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        f = open(p, "a+b")
        opened_here = True
        owned_path = p
    else:
        f = target

    fd = f.fileno()
    if sys.platform == "win32":
        import msvcrt

        f.seek(0)
        mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
        msvcrt.locking(fd, mode, 1)
        try:
            yield f
        finally:
            f.seek(0)
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            finally:
                if opened_here:
                    f.close()
                    if cleanup and owned_path is not None:
                        _unlink_lock_file(owned_path)
    else:
        import fcntl

        mode = fcntl.LOCK_EX if blocking else (fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, mode)
        try:
            yield f
        finally:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                if opened_here:
                    f.close()
                    if cleanup and owned_path is not None:
                        _unlink_lock_file(owned_path)


def _atomic_write_text(path: Path, text: str) -> None:
    """Crash-safe atomic replacement via temporary file + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as tmp_file:
            tmp_file.write(text)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _sanitize_text(value: str, field_name: str, file_ref: str) -> str:
    """Validate and collapse multiline/control text into safe single-line text."""
    if value is None or "\x00" in value:
        raise TriageError(
            "INVALID_INPUT",
            file_ref,
            f"null byte or missing text in --{field_name}",
            "non-empty plain text without null bytes",
            f"invalid --{field_name}",
            f"supply clean non-empty text for --{field_name}",
        )
    cleaned = re.sub(r"[\r\n\t]+", " ", value).strip()
    cleaned = re.sub(r"(?<!\\)\|", r"\|", cleaned)
    if not cleaned:
        raise TriageError(
            "INVALID_INPUT",
            file_ref,
            f"--{field_name} cannot be empty",
            f"non-empty value for --{field_name}",
            f"empty --{field_name}",
            f"provide non-empty text for --{field_name}",
        )
    return cleaned


def _validate_id(entry_id: str, file_ref: str) -> str:
    if not entry_id or "\x00" in entry_id or not _SAFE_ID_RE.match(entry_id):
        raise TriageError(
            "INVALID_INPUT",
            file_ref,
            "triage --id violates safe identifier grammar",
            "alphanumeric prefix with [A-Za-z0-9._:-] (1..64 chars, no spaces/slashes)",
            f"refused --id: {entry_id!r}",
            "re-run with a clean ID such as INC-101 or DIAG-1",
        )
    return entry_id


def _validate_token(value: str, flag_name: str, file_ref: str) -> str:
    if not value or "\x00" in value or not _SAFE_TOKEN_RE.match(value):
        raise TriageError(
            "INVALID_INPUT",
            file_ref,
            f"--{flag_name} contains whitespace or invalid characters",
            "single-line identifier without spaces or control chars",
            f"refused --{flag_name}: {value!r}",
            f"pass a valid --{flag_name} identifier",
        )
    return value


def _validate_evidence_observed(observed: str, file_ref: str) -> str:
    cleaned = _sanitize_text(observed, "observed", file_ref)
    normalized = cleaned.strip().lower()
    if normalized in _PLACEHOLDER_VALUES:
        raise TriageError(
            "INVALID_EVIDENCE",
            file_ref,
            "observed evidence cannot be an empty or placeholder value",
            "concrete command output, exit code, or measured artifact observation",
            f"placeholder --observed: {observed!r}",
            "capture real command output before recording evidence",
        )
    return cleaned


def _resolve_safe_path(
    raw_path: str,
    repo_root: Optional[Path] = None,
    *,
    must_exist: bool = False,
    missing_code: str = "INVALID_ARTIFACT",
) -> Path:
    """Resolve and enforce path traversal + symlink containment."""
    if not raw_path or "\x00" in raw_path:
        raise TriageError(
            "PATH_SECURITY",
            str(raw_path),
            "empty path or null byte rejected",
            "clean filesystem path",
            f"invalid path: {raw_path!r}",
            "supply a valid non-empty path",
        )
    candidate = Path(raw_path)

    if not candidate.is_absolute() and ".." in candidate.parts:
        raise TriageError(
            "PATH_SECURITY",
            raw_path,
            "relative path traversal ('..') is prohibited",
            "path without parent-directory traversal",
            f"traversal rejected: '{raw_path}'",
            "use a normalized path without '..'",
        )

    if candidate.is_symlink():
        raise TriageError(
            "PATH_SECURITY",
            raw_path,
            "direct symlink targets are refused by security containment",
            "regular non-symlink path",
            f"symlink refused: '{raw_path}'",
            "point directly to the regular target file",
        )

    if repo_root is not None:
        base = repo_root.resolve()
        joined = candidate if candidate.is_absolute() else (repo_root / candidate)
        # Walk intermediate relative segments inside repo_root to detect nested symlinks.
        if joined.is_relative_to(repo_root) if hasattr(joined, "is_relative_to") else True:
            try:
                rel_parts = joined.relative_to(repo_root).parts
                cur = repo_root
                for part in rel_parts:
                    cur = cur / part
                    if cur.is_symlink():
                        raise TriageError(
                            "PATH_SECURITY",
                            raw_path,
                            "symlink traversal inside repo-root refused",
                            f"non-symlink path inside '{base}'",
                            f"symlink component: '{cur}'",
                            "use a real path inside --repo-root without symlinks",
                        )
            except ValueError:
                pass
        resolved = joined.resolve()
        if not resolved.is_relative_to(base):
            raise TriageError(
                "PATH_SECURITY",
                raw_path,
                "target path escapes --repo-root boundary",
                f"path contained inside '{base}'",
                f"resolved path '{resolved}' escapes root",
                "restrict target paths inside --repo-root",
            )
    else:
        resolved = candidate.resolve()

    if resolved.exists() and resolved.is_dir():
        raise TriageError(
            missing_code,
            raw_path,
            "target path points to a directory instead of a file",
            "regular file path",
            f"directory given: '{raw_path}'",
            "pass a file path",
        )

    if must_exist and not resolved.is_file():
        raise TriageError(
            missing_code,
            raw_path,
            "required target file does not exist",
            "existing regular file",
            f"missing file: '{raw_path}'",
            "verify the file path and create or build it first",
        )

    return resolved


def _read_tasks_text(tasks_path: Path) -> str:
    try:
        return tasks_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise TriageError(
            "STALE_INPUT",
            str(tasks_path),
            "tasks file is not readable UTF-8 text",
            "valid UTF-8 Markdown file",
            f"read/decode error: {exc}",
            "restore or fix encoding in tasks.md before running triage",
        ) from exc


def _extract_artifact_meta(artifact_path: Path) -> Dict[str, Any]:
    stat = artifact_path.stat()
    raw = artifact_path.read_bytes()
    mtime_utc = datetime.datetime.fromtimestamp(
        stat.st_mtime, tz=datetime.timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "path": str(artifact_path).replace("\\", "/"),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "mtime_utc": mtime_utc,
    }


def _strip_inline_code(text: str) -> str:
    return _INLINE_CODE_RE.sub("", text)


def _is_meaningful_evidence(payload: str) -> bool:
    cleaned = payload.strip()
    if not cleaned:
        return False
    # Check observed= field if structured, otherwise raw string
    obs_match = re.search(r"observed=`([^`]*)`", cleaned)
    if obs_match:
        val = obs_match.group(1).strip().lower()
    else:
        val = cleaned.lower()
    return val not in _PLACEHOLDER_VALUES


def _parse_task_blocks(content: str) -> List[Dict[str, Any]]:
    """Deterministically parse top-level task blocks outside code fences."""
    lines = content.splitlines()
    blocks: List[Dict[str, Any]] = []
    in_fence = False
    idx = 0

    while idx < len(lines):
        line = lines[idx]
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            idx += 1
            continue
        if in_fence:
            idx += 1
            continue

        top_match = _TOP_TASK_RE.match(line)
        if not top_match:
            idx += 1
            continue

        status_char = top_match.group(1)
        rest = top_match.group(2)
        end = idx + 1
        while end < len(lines):
            nxt = lines[end]
            if _FENCE_RE.match(nxt):
                break
            if nxt.strip() == "":
                # Peek ahead: keep scanning if next non-blank line is indented sub-item
                look = end + 1
                while look < len(lines) and lines[look].strip() == "":
                    look += 1
                if look < len(lines) and len(lines[look]) > len(lines[look].lstrip()):
                    end = look
                    continue
                break
            if len(nxt) == len(nxt.lstrip()):
                break
            end += 1

        # Trim trailing blank lines from end
        block_end = end
        while block_end > idx + 1 and lines[block_end - 1].strip() == "":
            block_end -= 1

        blocks.append({
            "start": idx,
            "end": block_end,
            "status": f"[{status_char}]",
            "status_char": status_char,
            "header": line,
            "rest": rest,
            "sublines": lines[idx + 1 : block_end],
        })
        idx = block_end

    return blocks


def _analyze_diagnostic_block(block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Inspect a parsed task block and return diagnostic info if it is an incident/probe item."""
    rest = block["rest"]
    status_char = block["status_char"]
    clean_rest = _strip_inline_code(rest)

    structured = _PROBE_OR_FIX_RE.match(rest)
    entry_kind = None
    entry_id: Optional[str] = None
    if structured:
        entry_kind = structured.group(1)
        entry_id = structured.group(3)
    else:
        id_match = _INCIDENT_ID_RE.search(clean_rest)
        if id_match:
            entry_id = id_match.group(1)

    markers: List[str] = []
    if status_char == "?":
        markers.append("- [?]")
    if entry_kind == "PROBE" or _LEADING_PROBE_FIX_TEXT_RE.match(clean_rest):
        tag_m = _LEADING_PROBE_FIX_TEXT_RE.match(clean_rest)
        if entry_kind == "PROBE" or (tag_m and tag_m.group(1) == "PROBE"):
            markers.append("PROBE")
        elif entry_kind == "FIX" or (tag_m and tag_m.group(1) == "FIX"):
            markers.append("FIX")
    if entry_id is not None:
        markers.append(entry_id)
    for cm in _CLAIM_MARKER_RE.findall(clean_rest):
        markers.append(cm)

    if not markers:
        return None

    declared_revs = 0
    hypotheses = 0
    evidences = 0
    trailing_hypotheses = 0
    evidence_texts: List[str] = []

    for sub in block["sublines"]:
        rm = _REVISIONS_SUB_RE.match(sub)
        if rm:
            declared_revs = max(declared_revs, int(rm.group(1)))
            continue
        if _HYPOTHESIS_SUB_RE.match(sub):
            hypotheses += 1
            trailing_hypotheses += 1
            continue
        em = _EVIDENCE_SUB_RE.match(sub)
        if em and _is_meaningful_evidence(em.group(1)):
            evidences += 1
            trailing_hypotheses = 0
            evidence_texts.append(em.group(1).strip())

    revisions = max(declared_revs, hypotheses)
    unverified_revs = (
        revisions if evidences == 0 else trailing_hypotheses
    )
    has_active_evidence = evidences > 0 and trailing_hypotheses == 0

    return {
        "id": entry_id or f"line-{block['start'] + 1}",
        "explicit_id": entry_id,
        "line": block["start"] + 1,
        "status": block["status"],
        "kind": entry_kind,
        "header": block["header"],
        "markers": sorted(set(markers)),
        "revisions": revisions,
        "evidence_count": evidences,
        "trailing_unverified_hypotheses": unverified_revs,
        "verified": has_active_evidence,
        "evidence_texts": evidence_texts,
        "block": block,
    }


def _find_insertion_index(lines: List[str]) -> int:
    for idx, line in enumerate(lines):
        if line.strip().startswith("## Delegated Subtasks and Blockers"):
            # Insert before preceding separator '---' if directly above
            insert_at = idx
            while insert_at > 0 and lines[insert_at - 1].strip() in ("", "---"):
                insert_at -= 1
            return insert_at
    return len(lines)


def _format_now_hm() -> str:
    # Derive YYYY-MM-DD HH:MM from ADR #22 _utc_now_iso so UTC helper stays single-sourced
    iso = _utc_now_iso()
    return iso[:10] + " " + iso[11:16]


def cmd_probe(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    tasks_path = _resolve_safe_path(
        args.tasks, repo_root, must_exist=False, missing_code="STALE_INPUT"
    )
    entry_id = _validate_id(args.id, str(tasks_path))
    actor = _validate_token(args.actor, "actor", str(tasks_path))
    symptom = _sanitize_text(args.symptom, "symptom", str(tasks_path))
    hypothesis = _sanitize_text(args.hypothesis, "hypothesis", str(tasks_path))
    discriminator = _sanitize_text(args.discriminator, "discriminator", str(tasks_path))

    lock_path = tasks_path.with_name(f"{tasks_path.name}.lock")
    with file_lock(lock_path, blocking=True, cleanup=True):
        if not tasks_path.exists() or tasks_path.stat().st_size == 0:
            content = DEFAULT_TASKS_HEADER
        else:
            content = _read_tasks_text(tasks_path)
            if not content.strip():
                content = DEFAULT_TASKS_HEADER

        blocks = _parse_task_blocks(content)
        matching: Optional[Dict[str, Any]] = None
        for b in blocks:
            info = _analyze_diagnostic_block(b)
            if info and info["explicit_id"] == entry_id:
                matching = info
                break

        now_hm = _format_now_hm()
        lines = content.splitlines()

        if matching is not None:
            if matching["kind"] == "FIX" or matching["block"]["status_char"].lower() == "x":
                raise TriageError(
                    "INVALID_STATE",
                    str(tasks_path),
                    f"entry '{entry_id}' is already promoted or closed",
                    "an open diagnostic PROBE entry or new ID",
                    f"status is '{matching['status']}'",
                    "open a new incident ID if diagnosing a separate issue",
                )
            if matching["trailing_unverified_hypotheses"] >= 1:
                revs_count = max(matching["revisions"], matching["trailing_unverified_hypotheses"])
                raise TriageError(
                    "TRIAGE_CIRCUIT_BREAKER",
                    str(tasks_path),
                    "diagnostic hypothesis revised twice without new empirical evidence",
                    "record empirical evidence via record-evidence before revising hypothesis",
                    f"id '{entry_id}' already has {revs_count} unverified revision(s) with no new evidence",
                    "stop guessing; run the discriminator command and run record-evidence, or emit a mode: investigate Handoff Packet",
                )

            new_rev = matching["revisions"] + 1
            b = matching["block"]
            new_header = f"- [?] PROBE [{actor} @ {now_hm}] {entry_id}: {symptom}"
            updated_subs: List[str] = []
            saw_rev_line = False
            for sub in b["sublines"]:
                if _REVISIONS_SUB_RE.match(sub):
                    updated_subs.append(f"  - revisions: {new_rev}")
                    saw_rev_line = True
                else:
                    updated_subs.append(sub)
            if not saw_rev_line:
                updated_subs.insert(0, f"  - revisions: {new_rev}")
            updated_subs.append(f"  - hypothesis [{new_rev}]: {hypothesis}")
            updated_subs.append(f"  - discriminator [{new_rev}]: {discriminator}")

            new_lines = lines[: b["start"]] + [new_header] + updated_subs + lines[b["end"] :]
        else:
            new_rev = 1
            entry_lines = [
                f"- [?] PROBE [{actor} @ {now_hm}] {entry_id}: {symptom}",
                f"  - revisions: {new_rev}",
                f"  - hypothesis [{new_rev}]: {hypothesis}",
                f"  - discriminator [{new_rev}]: {discriminator}",
            ]
            insert_at = _find_insertion_index(lines)
            prefix = lines[:insert_at]
            suffix = lines[insert_at:]
            if prefix and prefix[-1].strip() != "":
                new_lines = prefix + entry_lines + ([""] + suffix if suffix else [])
            else:
                new_lines = prefix + entry_lines + ([""] + suffix if suffix else [])

        _atomic_write_text(tasks_path, "\n".join(new_lines).rstrip() + "\n")

    print(f"[OK] Recorded probe {entry_id} (revision {new_rev}) in {tasks_path}")
    return 0


def cmd_record_evidence(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    tasks_path = _resolve_safe_path(
        args.tasks, repo_root, must_exist=True, missing_code="TASKS_NOT_FOUND"
    )
    entry_id = _validate_id(args.id, str(tasks_path))
    actor = _validate_token(args.actor, "actor", str(tasks_path))
    command = _sanitize_text(args.command, "command", str(tasks_path)).replace("`", "'")
    observed = _validate_evidence_observed(args.observed, str(tasks_path)).replace("`", "'")

    artifact_clause = ""
    if args.artifact:
        artifact_path = _resolve_safe_path(
            args.artifact, repo_root, must_exist=True, missing_code="INVALID_ARTIFACT"
        )
        meta = _extract_artifact_meta(artifact_path)
        artifact_clause = (
            f" | artifact={meta['path']} "
            f"(size_bytes={meta['size_bytes']}, sha256={meta['sha256']}, mtime_utc={meta['mtime_utc']})"
        )

    lock_path = tasks_path.with_name(f"{tasks_path.name}.lock")
    with file_lock(lock_path, blocking=True, cleanup=True):
        content = _read_tasks_text(tasks_path)
        blocks = _parse_task_blocks(content)
        matching = None
        for b in blocks:
            info = _analyze_diagnostic_block(b)
            if info and info["explicit_id"] == entry_id:
                matching = info
                break

        if matching is None:
            raise TriageError(
                "TRIAGE_ID_NOT_FOUND",
                str(tasks_path),
                f"diagnostic entry '{entry_id}' not found",
                f"existing diagnostic entry with ID '{entry_id}'",
                f"missing '{entry_id}' in {tasks_path}",
                f"run 'triage_incident.py probe --id {entry_id} ...' first",
            )

        now_hm = _format_now_hm()
        evidence_line = (
            f"  - evidence [{actor} @ {now_hm}]: cmd=`{command}` | observed=`{observed}`{artifact_clause}"
        )
        lines = content.splitlines()
        b = matching["block"]
        new_lines = lines[: b["end"]] + [evidence_line] + lines[b["end"] :]
        _atomic_write_text(tasks_path, "\n".join(new_lines).rstrip() + "\n")

    print(f"[OK] Recorded evidence for {entry_id} in {tasks_path}{artifact_clause}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    tasks_path = _resolve_safe_path(
        args.tasks, repo_root, must_exist=True, missing_code="TASKS_NOT_FOUND"
    )
    entry_id = _validate_id(args.id, str(tasks_path))
    actor = _validate_token(args.actor, "actor", str(tasks_path))
    target_role = _validate_token(args.target_role, "target-role", str(tasks_path))
    root_cause = _sanitize_text(args.root_cause, "root-cause", str(tasks_path))
    fix_scope = _sanitize_text(args.fix_scope, "fix-scope", str(tasks_path))

    lock_path = tasks_path.with_name(f"{tasks_path.name}.lock")
    with file_lock(lock_path, blocking=True, cleanup=True):
        content = _read_tasks_text(tasks_path)
        blocks = _parse_task_blocks(content)
        matching = None
        for b in blocks:
            info = _analyze_diagnostic_block(b)
            if info and info["explicit_id"] == entry_id:
                matching = info
                break

        if matching is None:
            raise TriageError(
                "TRIAGE_ID_NOT_FOUND",
                str(tasks_path),
                f"diagnostic entry '{entry_id}' not found",
                f"existing - [?] PROBE entry for '{entry_id}'",
                f"missing '{entry_id}'",
                f"register probe via 'triage_incident.py probe --id {entry_id} ...' first",
            )

        b = matching["block"]
        if matching["kind"] == "FIX" or b["status_char"].lower() != "?":
            raise TriageError(
                "INVALID_STATE",
                str(tasks_path),
                f"entry '{entry_id}' is not an open - [?] PROBE entry",
                "status '- [?] PROBE'",
                f"current header '{b['header']}'",
                "check task status before promoting",
            )

        if not matching["verified"]:
            if matching["evidence_count"] == 0:
                msg = f"cannot promote '{entry_id}' to FIX without recorded empirical evidence"
                expected = "at least one verified '- evidence ...:' block"
                actual = "0 recorded evidence entries"
                next_hint = f"run discriminator command and log via 'triage_incident.py record-evidence --id {entry_id} ...' first"
            else:
                msg = (
                    f"cannot promote '{entry_id}' to FIX: trailing unverified hypothesis "
                    f"was added after the last recorded evidence"
                )
                expected = "verified '- evidence ...:' block recorded after the latest hypothesis revision"
                actual = (
                    f"{matching['evidence_count']} prior evidence entry(ies), "
                    f"{matching['trailing_unverified_hypotheses']} unverified trailing hypothesis revision(s)"
                )
                next_hint = (
                    f"verify the latest hypothesis with its discriminator and run "
                    f"'triage_incident.py record-evidence --id {entry_id} ...' before promoting"
                )
            raise TriageError(
                "EVIDENCE_REQUIRED",
                str(tasks_path),
                msg,
                expected,
                actual,
                next_hint,
            )

        now_hm = _format_now_hm()
        lines = content.splitlines()
        symptom_tail = ""
        m = _PROBE_OR_FIX_RE.match(b["rest"])
        if m and m.group(4):
            symptom_tail = m.group(4).strip()

        new_header = f"- [ ] FIX [{actor} @ {now_hm}] {entry_id}: {root_cause}"
        fix_lines = [
            f"  - root_cause: {root_cause}",
            f"  - fix_scope: {fix_scope}",
            f"  - target_role: {target_role}",
        ]
        new_lines = lines[: b["start"]] + [new_header] + b["sublines"] + fix_lines + lines[b["end"] :]
        _atomic_write_text(tasks_path, "\n".join(new_lines).rstrip() + "\n")

    goal_desc = f"Resolve verified defect {entry_id}" + (f" ({symptom_tail})" if symptom_tail else "")
    latest_ev = matching["evidence_texts"][-1]
    handoff = (
        f"### Task Handoff Package: [{actor} -> {target_role}]\n"
        f"- Original goal: {goal_desc}\n"
        f"- Completed work: Empirical triage recorded {matching['evidence_count']} verified evidence item(s) ({latest_ev})\n"
        f"- Handoff boundary: Verified root cause: {root_cause}; fix scoped strictly to {fix_scope}\n"
        f"- Recommended prompt for {target_role}: Fix verified defect {entry_id} ({root_cause}) within '{fix_scope}' and verify against recorded evidence in {tasks_path.name}.\n"
    )
    sys.stdout.write(handoff)
    return 0


def cmd_check_tasks(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    tasks_path = _resolve_safe_path(
        args.tasks, repo_root, must_exist=True, missing_code="TASKS_NOT_FOUND"
    )
    content = _read_tasks_text(tasks_path)
    blocks = _parse_task_blocks(content)

    verified_facts: List[Dict[str, Any]] = []
    unverified_hypotheses: List[Dict[str, Any]] = []
    thrashing_set: set[str] = set()
    unverified_id_counts: Dict[str, int] = {}

    for b in blocks:
        info = _analyze_diagnostic_block(b)
        if not info:
            continue
        item = {
            "id": info["id"],
            "line": info["line"],
            "status": info["status"],
            "header": info["header"],
            "markers": info["markers"],
            "revisions": info["revisions"],
            "evidence_count": info["evidence_count"],
        }
        if info["verified"]:
            verified_facts.append(item)
        else:
            unverified_hypotheses.append(item)
            if info["explicit_id"]:
                eid = info["explicit_id"]
                unverified_id_counts[eid] = unverified_id_counts.get(eid, 0) + 1
                if info["trailing_unverified_hypotheses"] >= 2 or (
                    info["revisions"] >= 2 and info["evidence_count"] == 0
                ):
                    thrashing_set.add(eid)

    for eid, cnt in unverified_id_counts.items():
        if cnt >= 2:
            thrashing_set.add(eid)

    thrashing_ids = sorted(thrashing_set)
    payload = {
        "tasks_file": str(tasks_path).replace("\\", "/"),
        "verified_facts": verified_facts,
        "unverified_hypotheses": unverified_hypotheses,
        "thrashing_ids": thrashing_ids,
        "summary": {
            "verified_count": len(verified_facts),
            "unverified_count": len(unverified_hypotheses),
            "thrashing_count": len(thrashing_ids),
        },
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Triage Tasks Audit: {tasks_path}")
        print(f"  Verified facts        : {len(verified_facts)}")
        print(f"  Unverified hypotheses : {len(unverified_hypotheses)}")
        print(f"  Thrashing IDs         : {thrashing_ids}")

    if args.strict and (unverified_hypotheses or thrashing_ids):
        raise TriageError(
            "UNVERIFIED_HYPOTHESES",
            str(tasks_path),
            "unverified diagnostic hypotheses or hypothesis thrashing detected in strict mode",
            "zero unverified hypotheses and zero thrashing IDs",
            f"unverified={len(unverified_hypotheses)}, thrashing={thrashing_ids}",
            "record empirical evidence for each open probe or downgrade unverified claims to HYPOTHESIS",
        )
    return 0


def cmd_artifact(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    art_path = _resolve_safe_path(
        args.path, repo_root, must_exist=True, missing_code="INVALID_ARTIFACT"
    )
    result = _extract_artifact_meta(art_path)

    if args.compare:
        cmp_path = _resolve_safe_path(
            args.compare, repo_root, must_exist=True, missing_code="INVALID_ARTIFACT"
        )
        cmp_meta = _extract_artifact_meta(cmp_path)
        result["compare_path"] = cmp_meta["path"]
        result["compare_size_bytes"] = cmp_meta["size_bytes"]
        result["compare_sha256"] = cmp_meta["sha256"]
        result["compare_mtime_utc"] = cmp_meta["mtime_utc"]
        result["comparison"] = (
            "IDENTICAL_BYTES" if result["sha256"] == cmp_meta["sha256"] else "DIFFERS"
        )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Artifact: {result['path']}")
        print(f"  size_bytes: {result['size_bytes']}")
        print(f"  sha256    : {result['sha256']}")
        print(f"  mtime_utc : {result['mtime_utc']}")
        if "comparison" in result:
            print(f"  compare   : {result['comparison']} (vs {result['compare_path']})")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Epistemic Incident Triage & Evidence Gate CLI (Wave K)."
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_probe = sub.add_parser("probe", help="Register or revise a - [?] PROBE entry with Circuit Breaker.")
    p_probe.add_argument("--tasks", required=True, help="Path to tasks.md")
    p_probe.add_argument("--actor", required=True, help="Qualified actor_id")
    p_probe.add_argument("--id", required=True, help="Incident/diagnostic ID (e.g., INC-1)")
    p_probe.add_argument("--symptom", required=True, help="Observed symptom summary")
    p_probe.add_argument("--hypothesis", required=True, help="Testable hypothesis")
    p_probe.add_argument("--discriminator", required=True, help="1-step discriminating probe command")
    p_probe.add_argument("--repo-root", default=None, help="Optional repo root containment boundary")

    p_ev = sub.add_parser("record-evidence", help="Attach verified empirical evidence to a probe.")
    p_ev.add_argument("--tasks", required=True, help="Path to tasks.md")
    p_ev.add_argument("--actor", required=True, help="Qualified actor_id")
    p_ev.add_argument("--id", required=True, help="Incident/diagnostic ID")
    p_ev.add_argument("--command", required=True, help="Executed verification command")
    p_ev.add_argument("--observed", required=True, help="Observed stdout/stderr/exit output")
    p_ev.add_argument("--artifact", default=None, help="Optional artifact file to hash/measure")
    p_ev.add_argument("--repo-root", default=None, help="Optional repo root containment boundary")

    p_prom = sub.add_parser("promote", help="Fail-closed promotion from PROBE to FIX with Handoff Packet.")
    p_prom.add_argument("--tasks", required=True, help="Path to tasks.md")
    p_prom.add_argument("--actor", required=True, help="Qualified actor_id")
    p_prom.add_argument("--id", required=True, help="Incident/diagnostic ID")
    p_prom.add_argument("--root-cause", required=True, help="Verified root cause backed by evidence")
    p_prom.add_argument("--fix-scope", required=True, help="Minimal fix file/module scope")
    p_prom.add_argument("--target-role", required=True, help="Target role ID for Handoff Packet")
    p_prom.add_argument("--repo-root", default=None, help="Optional repo root containment boundary")

    p_chk = sub.add_parser("check-tasks", help="Classify diagnostic entries in tasks.md.")
    p_chk.add_argument("--tasks", required=True, help="Path to tasks.md")
    p_chk.add_argument("--json", action="store_true", help="Emit JSON output")
    p_chk.add_argument("--strict", action="store_true", help="Exit 1 if unverified or thrashing entries exist")
    p_chk.add_argument("--repo-root", default=None, help="Optional repo root containment boundary")

    p_art = sub.add_parser("artifact", help="Inspect artifact bytes/hash/mtime and optionally compare.")
    p_art.add_argument("--path", required=True, help="Path to artifact file")
    p_art.add_argument("--compare", default=None, help="Optional reference/template file to compare bytes")
    p_art.add_argument("--json", action="store_true", help="Emit JSON output")
    p_art.add_argument("--repo-root", default=None, help="Optional repo root containment boundary")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1

    try:
        if args.subcommand == "probe":
            return cmd_probe(args)
        if args.subcommand == "record-evidence":
            return cmd_record_evidence(args)
        if args.subcommand == "promote":
            return cmd_promote(args)
        if args.subcommand == "check-tasks":
            return cmd_check_tasks(args)
        if args.subcommand == "artifact":
            return cmd_artifact(args)
        return 2
    except TriageError as exc:
        envelope = _error_envelope(
            exc.code,
            exc.file_ref,
            exc.reason,
            exc.expected,
            exc.actual,
            exc.next_step,
        )
        sys.stderr.write(envelope + "\n")
        sys.stderr.write(f"[ERROR] {exc.reason}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"[ERROR] Unexpected triage failure: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
