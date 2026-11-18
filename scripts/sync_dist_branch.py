#!/usr/bin/env python3
"""Distribution-branch sync: mirror the dist content of a source branch
(dev) into the distribution branch (main) without carrying the
self-installation artifacts (.agents/**) or working documents
(docs/superpowers/**, docs/archive/**).

Process item from the audit #3 triage (branch-sync automation, Steward).

Model: content mirror over a fixed path set, NOT a merge. For every
path in DIST_PATHS the script takes the source branch tree, subtracts
DIST_EXCLUDE prefixes, checks the files out into the current worktree
(which must be on --target), and removes dist-tracked files that no
longer exist in the source. No-op when the mirrored content already
matches. The result is committed (unless --no-commit) and optionally
pushed (--push).

Zero-dependency (Python 3.10+ stdlib + git subprocess), same contract as
the rest of the utility belt.

Usage:
  python scripts/sync_dist_branch.py --source origin/dev --target main            # dry-run
  python scripts/sync_dist_branch.py --source origin/dev --target main --execute  # stage + commit
  python scripts/sync_dist_branch.py --source origin/dev --target main --execute --push
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

DIST_PATHS = [
    ".github",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING.ru.md",
    "LICENSE",
    "README.md",
    "README.ru.md",
    "docs",
    "scripts",
    "skills",
    "templates",
    "tests",
]

# Working documents that stay on the source (dev) branch only.
DIST_EXCLUDE_PREFIXES = [
    "docs/superpowers/",
    "docs/archive/",
]

SELF_INSTALL_PREFIX = ".agents/"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def _git_ok(*args: str) -> subprocess.CompletedProcess:
    res = _git(*args)
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{res.stderr}")
    return res


def _source_file_set(source: str) -> List[str]:
    """All file paths in the source tree under DIST_PATHS, minus excludes."""
    files: List[str] = []
    for path in DIST_PATHS:
        res = _git("ls-tree", "-r", "--name-only", f"{source}::{path}" if False else f"{source}", "--", path)
        if res.returncode != 0:
            continue  # path absent in source branch entirely
        for line in res.stdout.splitlines():
            f = line.strip()
            if not f:
                continue
            if f.startswith(SELF_INSTALL_PREFIX):
                continue
            if any(f.startswith(pref) for pref in DIST_EXCLUDE_PREFIXES):
                continue
            files.append(f)
    return sorted(set(files))


def _current_target_files(target_paths: List[str]) -> List[str]:
    files: List[str] = []
    for path in target_paths:
        res = _git("ls-files", "--", path)
        files.extend(line.strip() for line in res.stdout.splitlines() if line.strip())
    return sorted(set(files))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mirror the distribution content of a source branch into the target branch (working tree)."
    )
    parser.add_argument("--source", default="origin/dev", help="Source branch ref (default: origin/dev)")
    parser.add_argument("--target", default="main", help="Target branch = the CURRENT working tree branch (default: main)")
    parser.add_argument("--execute", action="store_true", help="Stage the mirrored content (default: dry-run report only)")
    parser.add_argument("--commit", action="store_true", help="Commit the staged result (implies --execute)")
    parser.add_argument("--push", action="store_true", help="Push the target branch after commit (implies --commit)")
    args = parser.parse_args(argv)

    execute = args.execute or args.commit or args.push

    branch = _git_ok("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != args.target:
        raise SystemExit(
            f"refusing: current branch is '{branch}', expected '{args.target}'. "
            "Run this script with the target branch checked out."
    )

    source_files = _source_file_set(args.source)
    current_files = _current_target_files(DIST_PATHS)

    to_checkout = [f for f in source_files if f not in current_files or True]
    # checkout of an identical file is a no-op for git; the authoritative
    # diff is computed by git itself after staging:
    stale = [f for f in current_files if f not in set(source_files)]

    if execute:
        # Batch checkout in chunks to stay under argv limits.
        CHUNK = 40
        for i in range(0, len(to_checkout), CHUNK):
            _git_ok("checkout", args.source, "--", *to_checkout[i : i + CHUNK])
        if stale:
            CHUNK = 40
            for i in range(0, len(stale), CHUNK):
                _git_ok("rm", "-q", "-r", "--", *stale[i : i + CHUNK])
        _git_ok("add", "-A", "--", *DIST_PATHS)

    staged = _git("diff", "--cached", "--name-status")
    staged_lines = [l for l in staged.stdout.splitlines() if l.strip()]

    if not staged_lines:
        print(f"sync-dist: '{args.target}' already mirrors {args.source} dist content. No-op.")
        return 0

    updates = sum(1 for l in staged_lines if l.startswith(("M", "A")))
    deletes = sum(1 for l in staged_lines if l.startswith("D"))
    print(f"sync-dist plan: {updates} file update(s)/addition(s), {deletes} deletion(s).")
    for line in staged_lines[:20]:
        print("  ", line)
    if len(staged_lines) > 20:
        print(f"   ... and {len(staged_lines) - 20} more")

    if not execute:
        print("Dry-run only. Re-run with --execute to apply.")
        return 0

    source_sha = _git_ok("rev-parse", "--short", args.source).stdout.strip()
    _git_ok(
        "commit",
        "-m",
        f"sync-dist: mirror {args.source} dist content into {args.target}\n\n"
        f"Source: {args.source} @ {source_sha}\n"
        f"Updates: {updates}, deletions: {deletes}\n"
        f"Excluded: {SELF_INSTALL_PREFIX}*, {', '.join(DIST_EXCLUDE_PREFIXES)}*",
    )
    print(f"Committed dist sync on '{args.target}'.")
    if args.push:
        _git_ok("push", "origin", args.target)
        print(f"Pushed '{args.target}' to origin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
