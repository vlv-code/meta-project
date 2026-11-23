"""Wave J — Lane O lock-in tests: dispatcher works under BOTH runtime bindings.

Harnesses increasingly ship a native orchestrator (an agent provided by the
harness itself that launches and collects other agents inside one session).
On such a harness the ``agent-intake-dispatcher`` duties are performed by
that orchestrator; on a harness without one the dispatcher stays a standalone
role session. These tests lock the *Dispatcher Runtime Binding* documentation
into ``skills/manage-meta-project/SKILL.md``: the binding table (standalone
default listed first, orchestrator-hosted gated on the agreed
``delegation_level``), the never-inferred establishment rule, the identical
dispatcher contract in both bindings, and the binding clauses threaded
through Phases 4-7 and the role matrix — while naming NO specific harness
anywhere (orchestrator availability is a per-harness, per-installation fact).

Also locks: the host-runtime self-identification example uses real session
markers (``ZCODE_PROJECT_DIR`` / ``ZCODE_SESSION_ID``), and the original
Mandatory Dispatcher Rule sentence is preserved verbatim.

Zero-dependency: Python 3.10+ standard library only.
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = REPO_ROOT / "skills" / "manage-meta-project" / "SKILL.md"

BINDING_HEADING = "Dispatcher Runtime Binding (harness-dependent)"
MATRIX_HEADING = "#### 3. Open Competency Catalog"
FORBIDDEN_HARNESS_NAMES = (
    "zcode",
    "antigravity",
    "claude",
    "cursor",
    "codex",
    "gemini",
    "copilot",
    "windsurf",
)


def _phase(text, start_heading, end_heading):
    """Return the slice of ``text`` between two headings (or None).

    ``end_heading=None`` means "to the end of ``text``".
    """
    start = text.find(start_heading)
    if start == -1:
        return None
    if end_heading is None:
        return text[start:]
    end = text.find(end_heading, start)
    if end == -1:
        return None
    return text[start:end]


class TestDispatcherRuntimeBinding(unittest.TestCase):
    """The binding block in Phase 2: table, contract, establishment rule."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()

    def _line_at(self, needle):
        idx = self.text.find(needle)
        self.assertNotEqual(idx, -1, f"marker not found: {needle!r}")
        return self.lines[self.text[:idx].count("\n")]

    def test_dispatcher_matrix_row_names_the_orchestrator_executor(self):
        rows = [
            line
            for line in self.lines
            if line.startswith("| `agent-intake-dispatcher` |")
        ]
        self.assertEqual(len(rows), 1, "expected exactly one dispatcher matrix row")
        self.assertIn("native orchestrator", rows[0])
        self.assertIn("binding above", rows[0])

    def test_binding_block_sits_between_dispatcher_rule_and_role_matrix(self):
        binding = self.text.find(BINDING_HEADING)
        rule = self.text.find("Mandatory Dispatcher Rule")
        matrix = self.text.find(MATRIX_HEADING)
        self.assertNotEqual(binding, -1, "binding block heading missing")
        self.assertNotEqual(rule, -1, "Mandatory Dispatcher Rule missing")
        self.assertNotEqual(matrix, -1, "role matrix heading missing")
        self.assertGreater(binding, rule)
        self.assertLess(binding, matrix)

    def test_binding_table_lists_standalone_first(self):
        standalone_idx = self.text.find("| `standalone` (default) |")
        hosted_idx = self.text.find("| `orchestrator-hosted` |")
        self.assertNotEqual(standalone_idx, -1, "standalone binding row missing")
        self.assertNotEqual(hosted_idx, -1, "orchestrator-hosted binding row missing")
        self.assertLess(standalone_idx, hosted_idx)
        standalone_line = self._line_at("| `standalone` (default) |")
        hosted_line = self._line_at("| `orchestrator-hosted` |")
        self.assertIn("user-mediated handoff packages", standalone_line)
        self.assertIn("same dispatcher passport", hosted_line)

    def test_hosted_row_gates_dispatch_on_every_delegation_level(self):
        hosted_line = self._line_at("| `orchestrator-hosted` |")
        for token in (
            "delegation_level",
            "strictly_manual",
            "controlled",
            "autonomous",
        ):
            self.assertIn(token, hosted_line)

    def test_binding_is_never_inferred_and_defaults_to_standalone(self):
        self.assertIn(
            "never inferred from the harness name, environment variables "
            "or another installation's records",
            self.text,
        )
        self.assertIn("Unknown or absent orchestrator means `standalone`", self.text)

    def test_binding_block_names_no_specific_harness(self):
        block = _phase(self.text, BINDING_HEADING, MATRIX_HEADING)
        self.assertIsNotNone(block, "binding block slice not found")
        lowered = block.lower()
        for harness in FORBIDDEN_HARNESS_NAMES:
            self.assertNotIn(harness, lowered, f"harness named: {harness!r}")

    def test_contract_is_identical_in_both_bindings(self):
        intro_line = self._line_at("**" + BINDING_HEADING + ":**")
        for token in (
            "passport",
            "qualified `actor_id`",
            "verification policy",
            "identical in both bindings",
        ):
            self.assertIn(token, intro_line)

    def test_transient_subagents_stay_allowed(self):
        self.assertIn(
            "Transient subagents (rule 7) stay allowed under every binding",
            self.text,
        )


class TestBindingClausesInPhases(unittest.TestCase):
    """Binding guidance threaded through Phases 4, 5, 6 and 7."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.lines = cls.text.splitlines()

    def test_phase4_proposal_asks_for_the_binding(self):
        phase4 = _phase(self.text, "### Phase 4:", "### Phase 5:")
        self.assertIsNotNone(phase4, "Phase 4 slice not found")
        self.assertIn("Dispatcher binding", phase4)
        self.assertIn("default `standalone`", phase4)

    def test_phase5_appends_binding_clause_under_hosted(self):
        step5 = [
            line
            for line in self.lines
            if line.startswith("5. Generate the initial ready-to-use system prompt")
        ]
        self.assertEqual(len(step5), 1, "expected exactly one Phase 5 step 5 line")
        self.assertIn("orchestrator-hosted", step5[0])
        self.assertIn("append to every generated prompt", step5[0])

    def test_phase6_treats_orchestrator_load_as_manual_step(self):
        target = [
            line
            for line in self.lines
            if "Profile Created ≠ Loaded by Harness" in line
        ]
        self.assertEqual(len(target), 1, "expected exactly one invariant bullet")
        self.assertIn("orchestrator-hosted", target[0])
        self.assertIn("manual step", target[0])

    def test_rule2_points_hosted_dispatch_to_delegation_level(self):
        phase7 = _phase(self.text, "### Phase 7:", None)
        self.assertIsNotNone(phase7, "Phase 7 slice not found")
        self.assertIn(
            "Under the `orchestrator-hosted` dispatcher binding, "
            "role-to-role dispatch follows the agreed `delegation_level`",
            phase7,
        )


class TestHostIdentificationMarkers(unittest.TestCase):
    """Phase 1 anti-anchoring example must use real session markers."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_host_identification_example_uses_real_session_markers(self):
        self.assertNotIn("ZCODE_AGENT", self.text)
        self.assertIn("`ZCODE_PROJECT_DIR` / `ZCODE_SESSION_ID`", self.text)


class TestMandatoryDispatcherRulePreserved(unittest.TestCase):
    """Lock-in: the original dispatcher rule sentence stays verbatim."""

    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_mandatory_dispatcher_rule_keeps_its_original_sentence(self):
        self.assertIn(
            "Forbid leaving the user with an unrouted bundle of multiple "
            "isolated roles without a single point of entry.",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
