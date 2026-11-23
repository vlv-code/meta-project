#!/usr/bin/env python3
"""
Shared helpers for the scripts/ automation utilities (ADR #22).

Single source of truth for the small Wave E helpers that were previously
duplicated per script (``_error_envelope`` in 7 copies, ``_utc_now_iso`` in
the update engine plus 3 inline copies in the report engine). Consumers
import it through the mirror try/except pattern:

    try:  # package-style import (tests: from scripts.<name> import ...)
        from scripts._common import _error_envelope
    except ImportError:  # direct script execution: python scripts/<name>.py
        from _common import _error_envelope

Delivery contract (ADR #22): ``scripts/_common.py`` is a registered manifest
component and every script that imports it declares
``requires: ["scripts/_common.py"]`` — a subset deployment that selects the
script must select the helper module too. There is deliberately NO local
fallback definition: if ``_common`` is absent the ImportError propagates at
import time (honest fail-fast) instead of silently reviving a drifted copy.

Presentation-only contract: these helpers never alter decisions, refusal
payloads, exit codes, or rc semantics.

Zero-dependency: Python 3.10+ standard library only.
"""

from __future__ import annotations

import datetime
import os
from typing import Dict, Optional


# ---------------------------------------------------------------------------
# Host-harness detection — SINGLE SOURCE OF TRUTH (ADR #22).
#
# Consumed by scripts/inspect_meta_project.py AND scripts/verify_identity.py.
# verify_identity.py used to carry a stale second copy of this table
# (HARNESS_ENV_MAP with ZCODE_AGENT / CLAUDE_CODE / CODEX_AGENT markers and
# its own detect_host_harness) which returned None in a real ZCode session,
# so its "--actor Host harness mismatch" warning could never fire there.
#
# Mini-tail 2026-11-22 (host-detect false positive, found live on a REAL
# ZCode desktop session):
# 1. The zcode signature now leads with the REAL session markers
#    (ZCODE_PROJECT_DIR, ZCODE_SESSION_ID — set by every real ZCode session);
#    ZCODE_AGENT/ZCODE_WORKSPACE stay as legacy fallback (real sessions never
#    set them, so the old signature never matched).
# 2. zcode is ordered BEFORE claude-code: the ZCode desktop bridges
#    Claude-compatible variables (CLAUDE_PROJECT_DIR, CLAUDE_SESSION_ID) INTO
#    its own sessions, so a bridge-equipped zcode session previously matched
#    the claude-code signature first. A genuine claude-code session has
#    claude vars WITHOUT ZCODE_* — zcode-first resolves the overlap correctly
#    in both worlds.
# 3. CODEX_HOME is removed from the codex signature: it is machine-scoped
#    (set by a user-level Codex installation and leaking into ANY harness),
#    not session evidence. CODEX_AGENT remains the sole codex marker.
# 4. antigravity/cursor table audited for the same machine-scoped defect:
#    ANTIGRAVITY_APP_DATA_DIR is machine-scoped by nature but no live
#    evidence of foreign-session leakage exists; flagged in the lane report,
#    left unchanged pending evidence. Cursor variables are session/agent
#    scoped — clean.
HOST_HARNESS_SIGNATURES: list[tuple[str, tuple[str, ...]]] = [
    ("antigravity", ("ANTIGRAVITY_AGENT", "ANTIGRAVITY_APP_DATA_DIR", "AGY_BROWSER_WS_URL")),
    ("zcode", ("ZCODE_PROJECT_DIR", "ZCODE_SESSION_ID", "ZCODE_AGENT", "ZCODE_WORKSPACE")),
    ("cursor", ("CURSOR_AGENT", "CURSOR_TRACE", "CURSOR_VERSION")),
    ("claude-code", ("CLAUDE_CODE", "CLAUDE_PROJECT_DIR")),
    ("codex", ("CODEX_AGENT",)),
]


def detect_host_harness(env: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Deterministically detect host execution harness from environment variables.

    Signatures use SESSION-scoped variables only (machine-scoped variables
    leak across harnesses and cannot attest a session — see the
    HOST_HARNESS_SIGNATURES comment for the 2026-11-22 mini-tail).

    Checked signatures:
    - Antigravity: ANTIGRAVITY_AGENT, ANTIGRAVITY_APP_DATA_DIR, AGY_BROWSER_WS_URL
    - ZCode: ZCODE_PROJECT_DIR, ZCODE_SESSION_ID (+ legacy ZCODE_AGENT, ZCODE_WORKSPACE)
    - Cursor: CURSOR_AGENT, CURSOR_TRACE, CURSOR_VERSION
    - Claude Code: CLAUDE_CODE, CLAUDE_PROJECT_DIR
    - Codex: CODEX_AGENT (CODEX_HOME removed — machine-scoped)

    Returns canonical harness id (e.g. 'antigravity', 'zcode') or None.
    """
    target_env = os.environ if env is None else env
    for harness, env_vars in HOST_HARNESS_SIGNATURES:
        if any(target_env.get(var) for var in env_vars):
            return harness
    return None


def _error_envelope(
    code: str,
    file: str,
    reason: str,
    expected: str,
    actual: str,
    next_step: str,
) -> str:
    """Uniform Wave E error envelope (presentation ONLY).

    Returns the canonical leading line of a failure block:
        [CODE] <file>: <reason> | expected: <X> | actual: <Y> | next: <step>
    The envelope never alters gate/resolution/compaction/update/report
    decisions, refusal payloads, exit codes, or rc semantics — it wraps the
    existing structured refusals, which keep their full content on the
    following lines."""
    return (
        f"[{code}] {file}: {reason} | expected: {expected} | "
        f"actual: {actual} | next: {next_step}"
    )


def _utc_now_iso() -> str:
    """Canonical UTC timestamp used by reports, journals, and locks."""
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
