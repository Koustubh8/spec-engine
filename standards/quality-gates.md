# Quality Gates

Production readiness criteria applied before any spec-graph project ships.

## Gate 1: Spec Completeness

**Criteria:** Every spec has requirements, every requirement has scenarios.

**Check:**
```bash
python3 tools/knowledge-graph/lint.py
```

**Pass:** Zero SCENARIO_FOR_REQ warnings, zero NO_ORPHAN_REQUIREMENTS warnings.

## Gate 2: API Contract Completeness

**Criteria:** Every exposed endpoint has accepts, returns, and fails_with edges.

**Check:** Run the spec linter:
```bash
python3 tools/spec-studio/backend/spec_lint.py
```

**Pass:** Zero EXPOSES_HAS_CONTRACT errors.

## Gate 3: Production Readiness Score

**Criteria:** 10+ out of 12 production lint rules pass.

**Check:**
```bash
cd tools/spec-studio/backend
python3 prod_lint.py
```

**Score bands:**
- 12/12 🟢 Production ready — ship freely
- 10-11 🟡 Minor gaps — ship with tracking issues
- 7-9 🟠 Needs work — address before production
- 0-6 🔴 Not production ready — do NOT deploy

## Gate 4: Architecture Rationale

**Criteria:** Every architectural decision has a change node with rejected alternatives.

**Check:** Query the change node:
```bash
python3 tools/knowledge-graph/query.py "explore-<project>" --depth 2
```

**Pass:** The output shows `supersedes`, `blocks`, and `enables` edges documenting the decision.

## Gate 5: Dependency Impact Analysis

**Criteria:** Before merging a change, run impact analysis.

**Check:**
```bash
python3 tools/knowledge-graph/query.py "<changed-spec>" --depth 3
```

**Pass:** All affected components are identified and accounted for in the change proposal.

## Gate 6: Implementation Traceability

**Criteria:** Every code file implementing a spec has an `implements` edge.

**Check:** Query reverse implements edges or verify in the dashboard.

**Pass:** Code → spec mapping is queryable in both directions.

## Pre-Commit Checklist

Before committing spec changes:
1. Run `lint.py` — all errors resolved
2. Run `spec_lint.py` — all EXPOSES and EXPLORATION gates pass
3. Run `prod_lint.py` — score documented in change node
4. Impact analysis run and documented
5. All new nodes have valid frontmatter (title, kind, created, updated)
