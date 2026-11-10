#!/usr/bin/env python3
"""
Template Injection & Skill Parity Synchronizer.
Zero-dependency utility (pure Python 3.10+ standard library).
Injects canonical templates from templates/ into embedded sections of skills/,
and mirrors canonical skills/ into .agents/skills/.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Tuple

EMBEDDED_TARGETS: Dict[str, Dict[str, str]] = {
    "skills/init-meta-project/SKILL.md": {
        "boundaries.md": "templates/project_knowledge/boundaries.md",
        "observations.md": "templates/project_knowledge/observations.md",
        "weak_spots.md": "templates/project_knowledge/weak_spots.md",
        "AGENTS.md": "templates/AGENTS.md",
    },
    "skills/manage-meta-project/SKILL.md": {
        "profile.md": "templates/team/profile.md",
        "notes.md": "templates/team/notes.md",
        "system_prompt.md": "templates/team/system_prompt.md",
    },
}


def replace_embedded_template(
    text: str, tmpl_name: str, new_template_content: str
) -> Tuple[str, bool]:
    """
    Locates an embedded template block following:
      ### Template: `tmpl_name`
      ```markdown
      ...
      ```
    and replaces its inner body with new_template_content.
    Returns (updated_text, modified).
    """
    pattern = (
        rf"(###\s*Template:\s*`?{re.escape(tmpl_name)}`?\s*\n+```(?:[a-zA-Z0-9_\-]+)?\n)"
        rf"(.*?)"
        rf"(^```)"
    )
    match = re.search(pattern, text, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return text, False

    header = match.group(1)
    old_body = match.group(2)
    footer = match.group(3)

    clean_new_body = new_template_content.rstrip() + "\n"
    if old_body.strip() == clean_new_body.strip():
        return text, False

    new_text = text[:match.start()] + header + clean_new_body + footer + text[match.end():]
    return new_text, True


def sync_embedded_templates(
    repo_root: Path, write: bool = False
) -> Tuple[bool, List[str]]:
    """
    Synchronizes canonical templates from templates/ into embedded sections of skills/.
    Returns (in_sync, list_of_drift_messages).
    """
    drift_messages: List[str] = []

    for target_skill_rel, tmpl_map in EMBEDDED_TARGETS.items():
        skill_path = repo_root / target_skill_rel
        if not skill_path.is_file():
            continue

        content = skill_path.read_text(encoding="utf-8")
        original_content = content

        for tmpl_name, tmpl_rel in tmpl_map.items():
            tmpl_path = repo_root / tmpl_rel
            if not tmpl_path.is_file():
                continue

            canonical_content = tmpl_path.read_text(encoding="utf-8")
            updated, modified = replace_embedded_template(
                content, tmpl_name, canonical_content
            )
            if modified:
                drift_messages.append(
                    f"Drift: Embedded template '{tmpl_name}' in {target_skill_rel} diverges from {tmpl_rel}"
                )
                content = updated

        if write and content != original_content:
            skill_path.write_text(content, encoding="utf-8")

    in_sync = len(drift_messages) == 0
    return in_sync, drift_messages


def sync_skill_mirroring(
    repo_root: Path, write: bool = False
) -> Tuple[bool, List[str]]:
    """
    Ensures that every skill in skills/*/SKILL.md has an identical copy in .agents/skills/*/SKILL.md.
    Returns (in_sync, list_of_drift_messages).
    """
    drift_messages: List[str] = []
    skills_dir = repo_root / "skills"
    agent_skills_dir = repo_root / ".agents" / "skills"

    if not skills_dir.is_dir():
        return True, []

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        skill_name = skill_file.parent.name
        mirror_file = agent_skills_dir / skill_name / "SKILL.md"

        if not mirror_file.is_file():
            drift_messages.append(
                f"Drift: Missing mirrored skill at {mirror_file.relative_to(repo_root)}"
            )
            if write:
                mirror_file.parent.mkdir(parents=True, exist_ok=True)
                mirror_file.write_text(skill_file.read_text(encoding="utf-8"), encoding="utf-8")
            continue

        canonical_text = skill_file.read_text(encoding="utf-8")
        mirrored_text = mirror_file.read_text(encoding="utf-8")

        if canonical_text != mirrored_text:
            drift_messages.append(
                f"Drift: .agents/skills/{skill_name}/SKILL.md is out of sync with skills/{skill_name}/SKILL.md"
            )
            if write:
                mirror_file.write_text(canonical_text, encoding="utf-8")

    in_sync = len(drift_messages) == 0
    return in_sync, drift_messages


def run_sync(repo_root: Path, write: bool = False) -> Tuple[bool, List[str]]:
    """
    Executes full synchronization pass:
      1. Embed canonical templates into skills/.
      2. Mirror skills/ into .agents/skills/.
    """
    all_drifts: List[str] = []

    emb_ok, emb_drifts = sync_embedded_templates(repo_root, write=write)
    all_drifts.extend(emb_drifts)

    mir_ok, mir_drifts = sync_skill_mirroring(repo_root, write=write)
    all_drifts.extend(mir_drifts)

    in_sync = len(all_drifts) == 0
    return in_sync, all_drifts


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Template Injection & Skill Parity Synchronizer"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run check: verify that embedded templates and mirrored skills have zero drift",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write updates: inject canonical templates into skills/ and mirror to .agents/skills/",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Repository root directory (default: current working directory)",
    )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parser.parse_args(argv)

    if not args.check and not args.write:
        parser.print_help()
        sys.stderr.write("\nError: Must specify either --check or --write.\n")
        return 2

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()

    in_sync, drifts = run_sync(repo_root, write=args.write)

    if args.write:
        if in_sync:
            sys.stdout.write("Template Synchronizer: All templates and mirrored skills are already up to date.\n")
        else:
            sys.stdout.write(f"Template Synchronizer: Successfully synchronized {len(drifts)} item(s):\n")
            for d in drifts:
                sys.stdout.write(f"  [OK] {d}\n")
        return 0

    if args.check:
        if in_sync:
            sys.stdout.write("Template Synchronizer: 0 drift detected. Canonical templates and skills are in full parity.\n")
            return 0
        else:
            sys.stderr.write(f"Template Synchronizer: Drift detected in {len(drifts)} item(s):\n")
            for d in drifts:
                sys.stderr.write(f"  [FAIL] {d}\n")
            sys.stderr.write("\nRemedy: Run 'python scripts/sync_templates.py --write' to synchronize templates.\n")
            return 1


    return 0


if __name__ == "__main__":
    sys.exit(main())
