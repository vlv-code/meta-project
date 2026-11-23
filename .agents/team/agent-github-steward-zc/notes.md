# Workspace and Private Notes: GitHub Steward & Release Captain (`vlv-code/meta-project::zcode::zc-main::agent-github-steward`)

This document is dedicated exclusively to the in-depth working context, drafts, and role-specific specifications of the ZCode `agent-github-steward` instance (Actor: `vlv-code/meta-project::zcode::zc-main::agent-github-steward`).
No other agent is permitted to modify the contents of this file.

---

## 1. Role-Specific Invariants and Standards
- ZCode installation operates as a parallel copy of the canonical `agent-github-steward` role; the Antigravity instance at `.agents/team/agent-github-steward/` is read-only reference for this installation.

---

## 2. Working Drafts and Unfinished Research
- (Intermediate notes that do not bloat the global project context)

---

## 3. Registry of External Links and Documentation
- (Links to domain specifications, API documentation, and standards)

---

## Pending action: jwave_p lock test rewrite (blocked by a parallel live session, 2026-11-23)

`tests/test_jwave_p.py` is currently held/overwritten by a parallel live
session (writes revert within milliseconds). The ADR #23 closure of
scope items (4)/(5) is committed on dev in `c3db146` WITHOUT the lock
test update — as a result the file carries a temporary SyntaxError
(broken assignment, line ~165) and the old lock test still expects
`[OPEN 2026-11-23]` markers that no longer exist.

When the parallel session releases the file, apply (one shot, from the
repo root):

python - <<'PY'
import pathlib
p = pathlib.Path("tests/test_jwave_p.py")
b = p.read_bytes()
broken = b'body = "' + b'\n' + b'".join(self.lines[start:end])'
fixed = b'body = "' + b'\n' + b'".join(self.lines[start:end])'
if broken in b:
    b = b.replace(broken, fixed, 1)
    p.write_bytes(b)
    print("assignment literal fixed")
else:
    print("assignment already fixed")
PY

Then replace `test_adr_23_records_owner_definition_and_open_scope_items`
with the closed-semantics version (asserts [ЗАКРЫТО 2026-11-23] markers
covering docs/superpowers/plans and v1.0.0-alpha.7/v1.0.0-alpha.8,
assertNotIn [OPEN 2026-11-23]; the full replacement body was prepared
in-session and lost to the same race — re-create from the ADR text).
Then: full battery + push dev; sync-dist mirrors into main automatically.
