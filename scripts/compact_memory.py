#!/usr/bin/env python3
"""
Context Rot Shield & Memory Compactor.
Zero-dependency utility (pure Python 3.10+ standard library).
Rotates oversized observation tables and archived tasks into .agents/project_knowledge/archive/.
"""

from __future__ import annotations

import argparse
import contextlib
from datetime import datetime
import os
from pathlib import Path
import re
import sys
from typing import Any, List, Optional, Tuple, Union


@contextlib.contextmanager
def file_lock(target: Union[str, os.PathLike[str], Any], blocking: bool = True):
    """
    Cross-platform file locking context manager (Windows msvcrt / Unix fcntl).
    Accepts an open file object or a Path/str path.
    """
    opened_here = False
    if isinstance(target, (str, os.PathLike)):
        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        f = open(p, "a+b")
        opened_here = True
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


def compact_observations(
    content: str, max_rows: int = 20, keep_rows: int = 10
) -> Tuple[bool, str, str]:
    """
    Compacts observations.md if data rows exceed max_rows.
    Retains header + newest keep_rows in the primary file.
    Returns (compacted, new_primary_content, archive_chunk).
    """
    lines = content.splitlines()
    header_idx = -1
    sep_idx = -1

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if line_str.startswith("|") and ("Date" in line_str or "Дата" in line_str):
            header_idx = idx
            if idx + 1 < len(lines) and re.match(r"^\|\s*:?---+", lines[idx + 1].strip()):
                sep_idx = idx + 1
            break

    if header_idx == -1 or sep_idx == -1:
        return False, content, ""

    data_rows: List[str] = []
    end_table_idx = len(lines)

    for idx in range(sep_idx + 1, len(lines)):
        line = lines[idx]
        if line.strip().startswith("|"):
            data_rows.append(line)
        elif line.strip() == "":
            if idx + 1 < len(lines) and lines[idx + 1].strip().startswith("|"):
                continue
            else:
                end_table_idx = idx
                break
        else:
            end_table_idx = idx
            break

    if len(data_rows) <= max_rows:
        return False, content, ""

    def is_pinned(r: str) -> bool:
        return "[pin]" in r.lower()

    unpinned_indices = [idx for idx, r in enumerate(data_rows) if not is_pinned(r)]
    if len(unpinned_indices) <= keep_rows:
        return False, content, ""

    older_indices = set(unpinned_indices[:-keep_rows])
    retained_rows = [r for idx, r in enumerate(data_rows) if idx not in older_indices]
    older_rows = [data_rows[idx] for idx in unpinned_indices[:-keep_rows]]

    # Construct new primary content
    pre_table = lines[:sep_idx + 1]
    post_table = lines[end_table_idx:]

    archive_notice = (
        "> [!NOTE]\n"
        "> Historical observations compacted into `.agents/project_knowledge/archive/`.\n"
    )

    new_primary_lines = pre_table + retained_rows + [""] + [archive_notice] + post_table
    new_primary = "\n".join(new_primary_lines).rstrip() + "\n"

    # Construct archive chunk
    table_header = [lines[header_idx], lines[sep_idx]]
    archive_lines = table_header + older_rows
    archive_chunk = "\n".join(archive_lines) + "\n"

    return True, new_primary, archive_chunk


def compact_tasks(
    content: str, max_completed: int = 10, keep_completed: int = 5
) -> Tuple[bool, str, str]:
    """
    Compacts completed tasks (- [x]) in tasks.md when exceeding max_completed.
    Retains all pending tasks (- [ ]) and newest keep_completed completed tasks.
    Returns (compacted, new_primary_content, archive_chunk).
    """
    lines = content.splitlines()
    completed_indices: List[int] = []

    for idx, line in enumerate(lines):
        line_str = line.strip()
        if re.match(r"^-\s*\[x\]", line_str, re.IGNORECASE):
            completed_indices.append(idx)

    if len(completed_indices) <= max_completed:
        return False, content, ""

    rotate_indices = set(completed_indices[:-keep_completed])

    archive_lines: List[str] = []
    new_lines: List[str] = []
    inserted_notice = False

    for idx, line in enumerate(lines):
        if idx in rotate_indices:
            archive_lines.append(line)
            if not inserted_notice:
                new_lines.append(
                    "> [!NOTE]\n> Earlier completed tasks archived in `.agents/project_knowledge/archive/tasks_archive.md`.\n"
                )
                inserted_notice = True
        else:
            new_lines.append(line)

    new_primary = "\n".join(new_lines).rstrip() + "\n"
    archive_chunk = "\n".join(archive_lines) + "\n"

    return True, new_primary, archive_chunk


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Context Rot Shield: Compact observations and tasks into archive."
    )
    parser.add_argument(
        "--observations",
        type=str,
        default=".agents/project_knowledge/observations.md",
        help="Path to observations.md",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default=".agents/project_knowledge/tasks.md",
        help="Path to tasks.md",
    )
    parser.add_argument(
        "--archive-dir",
        type=str,
        default=".agents/project_knowledge/archive",
        help="Directory where archive files are stored",
    )
    parser.add_argument(
        "--max-observations",
        type=int,
        default=20,
        help="Maximum number of observation rows before compaction triggers",
    )
    parser.add_argument(
        "--keep-observations",
        type=int,
        default=10,
        help="Number of newest observation rows to keep in primary file",
    )
    parser.add_argument(
        "--max-completed-tasks",
        type=int,
        default=10,
        help="Maximum completed tasks before compaction triggers",
    )
    parser.add_argument(
        "--keep-completed-tasks",
        type=int,
        default=5,
        help="Number of completed tasks to retain in primary file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate compaction without modifying files on disk",
    )

    args = parser.parse_args(argv)

    archive_dir = Path(args.archive_dir)
    obs_path = Path(args.observations)
    tasks_path = Path(args.tasks)

    compacted_any = False

    # 1. Compact observations
    if obs_path.is_file():
        lock_path = obs_path.with_name(f"{obs_path.name}.lock")
        with file_lock(lock_path, blocking=True):
            obs_content = obs_path.read_text(encoding="utf-8")
            compacted, new_obs, archive_chunk = compact_observations(
                obs_content, max_rows=args.max_observations, keep_rows=args.keep_observations
            )
            if compacted:
                compacted_any = True
                current_month = datetime.now().strftime("%Y%m")
                archive_obs_file = archive_dir / f"observations_{current_month}.md"
                sys.stdout.write(f"Observations: compacting older rows into {archive_obs_file}\n")
                if not args.dry_run:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    if archive_obs_file.is_file():
                        existing = archive_obs_file.read_text(encoding="utf-8")
                        chunk_lines = [line for line in archive_chunk.splitlines() if line.strip()]
                        data_rows_to_append = chunk_lines[2:] if len(chunk_lines) >= 2 else []
                        rows_only = "\n".join(data_rows_to_append)
                        if rows_only:
                            archive_obs_file.write_text(existing.rstrip() + "\n" + rows_only + "\n", encoding="utf-8")
                    else:
                        header = f"# Archived Observations ({current_month})\n\n---\n\n"
                        archive_obs_file.write_text(header + archive_chunk, encoding="utf-8")
                    obs_path.write_text(new_obs, encoding="utf-8")
            else:
                sys.stdout.write("Observations: table within limits, no compaction needed.\n")
    else:
        sys.stdout.write(f"Observations: file '{obs_path}' not found, skipping.\n")

    # 2. Compact tasks
    if tasks_path.is_file():
        lock_path = tasks_path.with_name(f"{tasks_path.name}.lock")
        with file_lock(lock_path, blocking=True):
            tasks_content = tasks_path.read_text(encoding="utf-8")
            compacted, new_tasks, archive_chunk = compact_tasks(
                tasks_content,
                max_completed=args.max_completed_tasks,
                keep_completed=args.keep_completed_tasks,
            )
            if compacted:
                compacted_any = True
                archive_tasks_file = archive_dir / "tasks_archive.md"
                sys.stdout.write(f"Tasks: compacting completed tasks into {archive_tasks_file}\n")
                if not args.dry_run:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    if archive_tasks_file.is_file():
                        existing = archive_tasks_file.read_text(encoding="utf-8")
                        archive_tasks_file.write_text(existing.rstrip() + "\n" + archive_chunk, encoding="utf-8")
                    else:
                        header = "# Archived Completed Tasks\n\n---\n\n"
                        archive_tasks_file.write_text(header + archive_chunk, encoding="utf-8")
                    tasks_path.write_text(new_tasks, encoding="utf-8")
            else:
                sys.stdout.write("Tasks: completed tasks within limits, no compaction needed.\n")
    else:
        sys.stdout.write(f"Tasks: file '{tasks_path}' not found, skipping.\n")

    if args.dry_run:
        sys.stdout.write("[Dry-run complete: no changes were written to disk]\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
