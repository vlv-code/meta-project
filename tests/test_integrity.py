"""
Tests for Meta-Project skills, templates, and structural integrity.
Uses only Python standard library (unittest) to run in any environment with zero dependencies.
"""

from pathlib import Path
import re
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT_DIR / "templates"


class TestSkillsIntegrity(unittest.TestCase):
    """Checks that all skills have valid YAML frontmatter and required sections."""

    def test_skills_frontmatter_and_sections(self):
        skills_dir = ROOT_DIR / "skills"
        self.assertTrue(skills_dir.is_dir(), "skills directory not found")

        skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
        self.assertGreater(len(skill_dirs), 0, "No skills found in skills/")

        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"Missing SKILL.md in {skill_dir.name}")

            content = skill_file.read_text(encoding="utf-8")

            # Check YAML frontmatter presence
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
            self.assertIsNotNone(match, f"Invalid or missing YAML frontmatter in {skill_file}")

            frontmatter = match.group(1)
            body = match.group(2)

            # Check 'name:'
            name_match = re.search(r"^name:\s*([^\s]+)", frontmatter, re.MULTILINE)
            self.assertIsNotNone(name_match, f"'name' field missing in {skill_file}")
            self.assertEqual(
                name_match.group(1),
                skill_dir.name,
                f"Skill name '{name_match.group(1)}' does not match directory '{skill_dir.name}'",
            )

            # Check 'description:'
            self.assertIn("description:", frontmatter, f"'description' missing in {skill_file}")

            # Check required procedural sections (supports Russian and English variants)
            trigger_variants = [
                "## Когда вызывать навык",
                "## When to invoke skill",
                "## When to Invoke",
                "## When to invoke",
                "## When to Invoke Skill",
            ]
            self.assertTrue(
                any(variant in body for variant in trigger_variants),
                f"Missing trigger section in {skill_file}",
            )

            execution_variants = [
                "## Порядок выполнения",
                "## Execution steps",
                "## Execution order",
                "## Execution Steps",
                "## Execution Order",
            ]
            self.assertTrue(
                any(variant in body for variant in execution_variants),
                f"Missing execution section in {skill_file}",
            )

    def test_skills_parity_between_canonical_and_agent_copies(self):
        """Verify that every skill in skills/ has an identical copy in .agents/skills/."""
        skills_dir = ROOT_DIR / "skills"
        agent_skills_dir = ROOT_DIR / ".agents" / "skills"
        self.assertTrue(agent_skills_dir.is_dir(), ".agents/skills directory not found")

        for skill_dir in [d for d in skills_dir.iterdir() if d.is_dir()]:
            canonical_file = skill_dir / "SKILL.md"
            agent_file = agent_skills_dir / skill_dir.name / "SKILL.md"
            self.assertTrue(agent_file.is_file(), f"Missing agent skill copy for {skill_dir.name}")

            canonical_text = canonical_file.read_text(encoding="utf-8")
            agent_text = agent_file.read_text(encoding="utf-8")
            self.assertEqual(
                canonical_text,
                agent_text,
                f"Parity mismatch between skills/{skill_dir.name}/SKILL.md and .agents/skills/{skill_dir.name}/SKILL.md"
            )

    def test_init_meta_project_interactive_interview_protocol(self):
        """Verify that init-meta-project skill codifies the two-question interactive interview."""
        init_skill = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"
        content = init_skill.read_text(encoding="utf-8")
        self.assertIn("Interactive Calibration Interview", content)
        self.assertIn("Two-Question Protocol", content)
        self.assertIn("North Stars & Core Invariants", content)
        self.assertIn("Red Zone & Sensitive Paths", content)


class TestTemplatesIntegrity(unittest.TestCase):
    """Checks that all standard templates exist and contain required placeholders/sections."""

    def test_templates_exist(self):
        templates_dir = ROOT_DIR / "templates"
        self.assertTrue(templates_dir.is_dir(), "templates directory not found")

        agents_template = templates_dir / "AGENTS.md"
        self.assertTrue(agents_template.is_file(), "templates/AGENTS.md missing")
        content = agents_template.read_text(encoding="utf-8")
        self.assertIn("{{PROJECT_NAME}}", content)
        self.assertIn(".agents/project_knowledge/", content)

        pk_dir = templates_dir / "project_knowledge"
        self.assertTrue(pk_dir.is_dir(), "templates/project_knowledge missing")

        for required_file in ["architecture.md", "boundaries.md", "observations.md", "weak_spots.md", "tasks.md"]:
            file_path = pk_dir / required_file
            self.assertTrue(file_path.is_file(), f"Missing template {required_file}")
            self.assertGreater(file_path.stat().st_size, 0, f"Template {required_file} is empty")

        team_dir = templates_dir / "team"
        self.assertTrue(team_dir.is_dir(), "templates/team missing")
        for required_file in ["profile.md", "notes.md", "system_prompt.md"]:
            file_path = team_dir / required_file
            self.assertTrue(file_path.is_file(), f"Missing team template {required_file}")
            self.assertGreater(file_path.stat().st_size, 0, f"Team template {required_file} is empty")

        global_template = templates_dir / "global" / "AGENTS.md"
        self.assertTrue(global_template.is_file(), "templates/global/AGENTS.md missing")
        self.assertGreater(global_template.stat().st_size, 0, "templates/global/AGENTS.md is empty")

    def test_boundaries_zones(self):
        boundaries = ROOT_DIR / "templates" / "project_knowledge" / "boundaries.md"
        content = boundaries.read_text(encoding="utf-8")

        green_variants = ["Зеленая зона", "Зелёная зона", "Green zone", "Green Zone"]
        yellow_variants = ["Желтая зона", "Yellow zone", "Yellow Zone"]
        red_variants = ["Красная зона", "Red zone", "Red Zone"]

        self.assertTrue(
            any(variant in content for variant in green_variants),
            f"Missing Green zone header in {boundaries}",
        )
        self.assertTrue(
            any(variant in content for variant in yellow_variants),
            f"Missing Yellow zone header in {boundaries}",
        )
        self.assertTrue(
            any(variant in content for variant in red_variants),
            f"Missing Red zone header in {boundaries}",
        )

    def test_boundaries_default_deny_invariant(self):
        """Verify boundaries template contains the Default Deny / Black Zone rule."""
        boundaries_path = TEMPLATES_DIR / "project_knowledge" / "boundaries.md"
        content = boundaries_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Default Deny|Black Zone|Запрет по умолчанию|Черная зона", content, re.IGNORECASE),
            "boundaries.md template must define Default Deny / Black Zone rule"
        )

    def test_system_prompt_circuit_breaker_invariant(self):
        """Verify role system prompt template contains Circuit Breaker and Target State Audit."""
        prompt_path = TEMPLATES_DIR / "team" / "system_prompt.md"
        content = prompt_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Circuit Breaker|Стоп-кран|Circuit-breaker", content, re.IGNORECASE),
            "system_prompt.md template must define Circuit Breaker rule"
        )
        self.assertTrue(
            re.search(r"Target State Audit|Аудит состояния объекта", content, re.IGNORECASE),
            "system_prompt.md template must define Target State Audit rule"
        )
        self.assertTrue(
            re.search(r"Role Identity Invariance|Identity Invariance", content, re.IGNORECASE),
            "system_prompt.md template must define Role Identity Invariance rule"
        )

    def test_architecture_data_flow_section(self):
        """Verify architecture template contains Data Flow section."""
        arch_path = TEMPLATES_DIR / "project_knowledge" / "architecture.md"
        content = arch_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"Data Flow|Потоки данных|Pre-Flight Flow Tracing", content, re.IGNORECASE),
            "architecture.md template must define Data Flows section"
        )

    def test_init_meta_project_embedded_boundaries_parity(self):
        """Verify embedded boundaries template in init-meta-project contains all security critical paths."""
        init_skill_path = ROOT_DIR / "skills" / "init-meta-project" / "SKILL.md"
        content = init_skill_path.read_text(encoding="utf-8")

        critical_patterns = [
            r"src/billing/\*\*",
            r"src/payments/\*\*",
            r"src/crypto/\*\*",
            r"\*\.pem",
            r"\*\.key",
            r"config/secrets/\*\*",
            r"Default Deny|Black Zone",
        ]
        for pattern in critical_patterns:
            self.assertTrue(
                re.search(pattern, content),
                f"Embedded boundaries template in init-meta-project is missing critical pattern: {pattern}"
            )

    def test_team_profiles_have_valid_yaml_frontmatter(self):
        """Verify that templates/team/profile.md and active .agents/team/*/profile.md files have valid YAML frontmatter."""
        required_fields = ["name:", "role_id:", "description:", "tools:", "model:", "invocation_triggers:"]

        # 1. Check template
        template_profile = ROOT_DIR / "templates" / "team" / "profile.md"
        self.assertTrue(template_profile.is_file(), "templates/team/profile.md is missing")
        content = template_profile.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "templates/team/profile.md must start with YAML frontmatter delimiter '---'")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, "templates/team/profile.md missing closing frontmatter delimiter '---'")
        frontmatter = parts[1]
        for field in required_fields:
            self.assertIn(field, frontmatter, f"templates/team/profile.md frontmatter missing required field '{field}'")

        # 2. Check active team profiles
        team_dir = ROOT_DIR / ".agents" / "team"
        self.assertTrue(team_dir.is_dir(), ".agents/team directory is missing")
        for role_dir in team_dir.iterdir():
            if role_dir.is_dir() and role_dir.name != "archive":
                profile_path = role_dir / "profile.md"
                self.assertTrue(profile_path.is_file(), f"Profile missing for active role {role_dir.name}")
                p_content = profile_path.read_text(encoding="utf-8")
                self.assertTrue(
                    p_content.startswith("---"),
                    f"Profile for {role_dir.name} must start with YAML frontmatter delimiter '---'"
                )
                p_parts = p_content.split("---", 2)
                self.assertGreaterEqual(
                    len(p_parts), 3,
                    f"Profile for {role_dir.name} missing closing frontmatter delimiter '---'"
                )
                p_frontmatter = p_parts[1]
                for field in required_fields:
                    self.assertIn(
                        field, p_frontmatter,
                        f"Profile for {role_dir.name} frontmatter missing required field '{field}'"
                    )


class TestRepositoryCanons(unittest.TestCase):
    """Checks standard GitHub open source files and structure."""

    def test_canonical_files_exist(self):
        canonical_files = [
            ".gitignore",
            "LICENSE",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
            "README.md",
            ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/workflows/ci.yml",
        ]

        for rel_path in canonical_files:
            file_path = ROOT_DIR / rel_path
            self.assertTrue(file_path.is_file(), f"Canonical GitHub file {rel_path} is missing")
            self.assertGreater(file_path.stat().st_size, 0, f"File {rel_path} is empty")

    def test_ci_matrix_includes_python_310(self):
        """Verify that GitHub Actions CI matrix explicitly includes Python 3.10."""
        ci_path = ROOT_DIR / ".github" / "workflows" / "ci.yml"
        content = ci_path.read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r"['\"]3\.10['\"]", content),
            "CI workflow matrix in .github/workflows/ci.yml must include '3.10' for Python 3.10+ declaration"
        )

    def test_ci_workflow_enforces_boundary_gate(self):
        """Verify that GitHub Actions CI workflow includes the Boundary Gate check."""
        ci_path = ROOT_DIR / ".github" / "workflows" / "ci.yml"
        content = ci_path.read_text(encoding="utf-8")
        self.assertIn(
            "scripts/check_boundaries.py",
            content,
            "CI workflow .github/workflows/ci.yml must include scripts/check_boundaries.py step"
        )

    def test_boundary_gate_script_exists_and_functional(self):
        """Verify that scripts/check_boundaries.py exists and executes --help cleanly."""
        script_path = ROOT_DIR / "scripts" / "check_boundaries.py"
        self.assertTrue(script_path.is_file(), "scripts/check_boundaries.py is missing")
        import subprocess
        import sys
        res = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"check_boundaries.py --help failed: {res.stderr}")
        self.assertIn("Boundary Gate", res.stdout)

    def test_compact_memory_script_exists_and_functional(self):
        """Verify that scripts/compact_memory.py exists and executes --help cleanly."""
        script_path = ROOT_DIR / "scripts" / "compact_memory.py"
        self.assertTrue(script_path.is_file(), "scripts/compact_memory.py is missing")
        import subprocess
        import sys
        res = subprocess.run([sys.executable, str(script_path), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"compact_memory.py --help failed: {res.stderr}")
        self.assertIn("Context Rot Shield", res.stdout)

    def test_sync_templates_script_exists_and_check_passes(self):
        """Verify that scripts/sync_templates.py exists and --check passes with 0 drift."""
        script_path = ROOT_DIR / "scripts" / "sync_templates.py"
        self.assertTrue(script_path.is_file(), "scripts/sync_templates.py is missing")
        import subprocess
        import sys
        res = subprocess.run([sys.executable, str(script_path), "--check"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"sync_templates.py --check failed: {res.stderr}\n{res.stdout}")
        self.assertIn("0 drift", res.stdout)



if __name__ == "__main__":
    unittest.main()
