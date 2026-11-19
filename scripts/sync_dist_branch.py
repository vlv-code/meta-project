#!/usr/bin/env python3
"""Distribution-branch sync: mirror the dist content of a source branch
(dev) into the distribution branch (main) without carrying the
self-installation artifacts (.agents/**) or working documents
(docs/superpowers/**, docs/archive/**).

Process item from the audit #3 triage (branch-sync automation, Steward).

Model: content restore over a fixed path set with exclude pathspecs, NOT
a merge. The current worktree (checked out on --target) receives the
dist paths from --source via `git restore --worktree`; dist-tracked
files absent from the source are removed. No-op when the mirrored
content already matches. Result is committed (unless --no-commit) and
optionally pushed (--push).

Zero-dependency (Python 3.10+ stdlib + git subprocess), same contract as
the rest of the utility belt.

Usage:
  python scripts/sync_dist_branch.py --source origin/dev --target main              # dry-run
  python scripts/sync_dist_branch.py --source origin/dev --target main --execute    # restore + commit
  python scripts/sync_dist_branch.py --source origin/dev --target main --execute --push
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import List

DIST_PATHS = [
    ".claude-plugin",
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
    "plugin.json",
    "scripts",
    "skills",
    "templates",
    "tests",
]

# Working documents that stay on the source (dev) branch only. Passed to
# git as exclude pathspecs so restore/ls-tree skip them natively (no
# per-path argv quoting issues with non-ASCII names).
DIST_EXCLUDE_PATHSPECS = [
    ":(exclude).agents/**",
    ":(exclude)docs/superpowers/**",
    ":(exclude)docs/archive/**",
    ":(exclude)download/**",
]

SELF_INSTALL_PREFIX = ".agents/"
DIST_EXCLUDE_PREFIXES = (
    ".agents/",
    "docs/superpowers/",
    "docs/archive/",
    "download/",
)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")


def _git_ok(*args: str) -> subprocess.CompletedProcess:
    res = _git(*args)
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{res.stderr}")
    return res


def _pathspec_args() -> List[str]:
    return [*DIST_PATHS, *DIST_EXCLUDE_PATHSPECS]


def _source_dist_files(source: str) -> List[str]:
    res = _git_ok("ls-tree", "-r", "--name-only", "-z", source, "--", *DIST_PATHS)
    return [
        f
        for f in res.stdout.split("\0")
        if f and not any(f.startswith(pref) for pref in DIST_EXCLUDE_PREFIXES)
    ]


def _target_dist_files() -> List[str]:
    res = _git_ok("ls-files", "-z", "--", *DIST_PATHS)
    return [
        f
        for f in res.stdout.split("\0")
        if f and not any(f.startswith(pref) for pref in DIST_EXCLUDE_PREFIXES)
    ]


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Mirror the distribution content of a source branch into the target branch (working tree)."
    )
    parser.add_argument("--source", default="origin/dev", help="Source branch ref (default: origin/dev)")
    parser.add_argument("--target", default="main", help="Target branch = the CURRENT working tree branch (default: main)")
    parser.add_argument("--execute", action="store_true", help="Restore the mirrored content (default: dry-run report only)")
    parser.add_argument("--commit", action="store_true", help="Commit the restored result (implies --execute)")
    parser.add_argument("--push", action="store_true", help="Push the target branch after commit (implies --commit)")
    args = parser.parse_args(argv)

    execute = args.execute or args.commit or args.push

    branch = _git_ok("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != args.target:
        raise SystemExit(
            f"refusing: current branch is '{branch}', expected '{args.target}'. "
            "Run this script with the target branch checked out."
    )

    source_files = _source_dist_files(args.source)
    target_files = _target_dist_files()
    source_set = set(source_files)

    stale = [f for f in target_files if f not in source_set]

    plan = []
    if execute:
        # Restore in worktree; pathspec excludes keep dev-only documents out.
        _git_ok("restore", "--source", args.source, "--worktree", "--", *_pathspec_args())
        if stale:
            CHUNK = 40
            for i in range(0, len(stale), CHUNK):
                _git_ok("rm", "-q", "-f", "--", *stale[i : i + CHUNK])
        _git_ok("add", "-A", "--", *DIST_PATHS)
        staged = _git("diff", "--cached", "--name-status")
        plan = [l for l in staged.stdout.splitlines() if l.strip()]
    else:
        # Dry-run plan: files differing between HEAD and source (git diff
        # across branches restricted to the dist path set).
        diff = _git("diff", "--name-status", "HEAD", args.source, "--", *_pathspec_args())
        plan = [l for l in diff.stdout.splitlines() if l.strip()]
        plan = [f"{status}\t{path}" for status, path in (l.split("\t", 1) for l in plan)]
        plan.extend(f"D\t{f}" for f in stale if f not in set())
        plan = sorted(set(plan))

    if not plan:
        print(f"sync-dist: '{args.target}' already mirrors {args.source} dist content. No-op.")
        return 0

    updates = sum(1 for l in plan if not l.startswith("D"))
    deletes = sum(1 for l in plan if l.startswith("D"))
    print(f"sync-dist plan: {updates} file update(s)/addition(s), {deletes} deletion(s).")
    for line in plan[:20]:
        print("  ", line.replace("\t", "  "))
    if len(plan) > 20:
        print(f"   ... and {len(plan) - 20} more")

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
        f"Excluded: {SELF_INSTALL_PREFIX}*, {', '.join(DIST_EXCLUDE_PATHSPECS)}",
    )
    print(f"Committed dist sync on '{args.target}'.")
    if args.push:
        _git_ok("push", "origin", args.target)
        print(f"Pushed '{args.target}' to origin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
