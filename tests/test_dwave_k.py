"""Wave D, Lane K — canonical-manifest contract tests (T5.4).

The canonical ``templates/release_manifest.json`` is the ship list the
update engine materializes as an INTEGRAL bundle. Its contract:

* every component ``path`` must be a real FILE — a directory-kind entry
  (trailing ``/``) makes the engine refuse the bundle outright
  (``PartialCacheError`` in ``_read_bundle_tree`` / missing git blob in
  ``_fetch_pinned_tree``) — defect D4;
* the updater ``scripts/update_meta_project.py`` must ship WITH the
  framework, otherwise a fresh install has no update engine — defect D5;
* ``framework_version`` must parse as semver 2.0.0 (machine-comparable
  release hygiene);
* every component path must exist in the repository tree at release time.

This test class is the coverage hole whose absence let D4/D5 ship in the
wave-0.9.0 C1 finding. Zero-dependency: Python 3.10+ stdlib only.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "templates" / "release_manifest.json"
UPDATER_PATH = "scripts/update_meta_project.py"

# Official semver 2.0.0 grammar (https://semver.org), stdlib-only.
_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def _component_paths(components):
    """Paths as the engine sees them (``_components_of`` drops entries
    with an empty/absent ``path``)."""
    return [str(c.get("path", "")) for c in components if str(c.get("path", ""))]


class CanonicalManifestContract(unittest.TestCase):
    """Contract on the CANONICAL templates/release_manifest.json."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.components = cls.manifest.get("components") or []
        cls.paths = _component_paths(cls.components)

    def test_every_component_is_file_kind(self):
        """No directory-kind entries remain (D4): no trailing slash, and
        each path resolves to an actual file in the repo tree."""
        dir_kind = [p for p in self.paths if p.endswith("/")]
        self.assertEqual(
            dir_kind, [], f"directory-kind components remain in manifest: {dir_kind}"
        )

    def test_updater_is_registered_component(self):
        """D5: the update engine ships as a manifest component."""
        self.assertIn(
            UPDATER_PATH,
            self.paths,
            f"{UPDATER_PATH} missing from canonical manifest components",
        )

    def test_framework_version_is_semver(self):
        version = str(self.manifest.get("framework_version", ""))
        self.assertIsNotNone(
            _SEMVER_RE.match(version),
            f"framework_version {version!r} does not parse as semver 2.0.0",
        )

    def test_all_component_paths_exist_in_repo_tree(self):
        missing = [p for p in self.paths if not (REPO_ROOT / p).is_file()]
        self.assertEqual(
            missing, [], f"manifest component paths absent from repo tree: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
