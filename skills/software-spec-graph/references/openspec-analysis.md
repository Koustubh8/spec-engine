# OpenSpec Analysis

Deep-dive into [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) (46k stars, MIT, August 2025) — the dominant spec-driven development framework for AI coding agents. This document captures what we learned, what we adapted, and what we improved.

## OpenSpec's Model

```
openspec/
├── specs/               ← source of truth (Requirements + Scenarios)
│   └── auth/spec.md     ← Given-When-Then format
│
└── changes/             ← proposed modifications
    └── add-2fa/
        ├── proposal.md  ← why + scope
        ├── design.md    ← technical approach
        ├── tasks.md     ← implementation checklist
        └── specs/        ← delta specs (ADDED/MODIFIED/REMOVED)
```

Flow: propose → spec → design → tasks → implement → verify → archive

## What OpenSpec Gets Right

1. **Delta-based specs** — ADDED/MODIFIED/REMOVED sections for brownfield work
2. **Separation of concerns** — spec (what) ≠ design (how) ≠ tasks (steps)
3. **Scenario format** — Given-When-Then, directly testable
4. **Change folders** — parallel work without conflicts
5. **Schema-driven** — artifact dependency graph (proposal→specs→design→tasks)
6. **Archive as merge** — deltas merge into source of truth
7. **Progressive rigor** — lite spec vs full spec
8. **Fluid, not rigid** — no phase gates, iterate freely

## What OpenSpec Lacks (Our Improvements)

| OpenSpec Gap | Our Graph Solution |
|-------------|-------------------|
| No graph/traversal | BFS + path finding across all specs |
| No typed predicates | 17 spec predicates (exposes, accepts, returns, etc.) |
| No contract edges | `exposes` + `accepts` + `returns` = complete interface |
| No verification edges | `tests`, `guarantees`, `implements` close the loop |
| No event causality | `triggers` captures pub/sub wiring |
| No inter-spec relationships | `depends_on`, `constrains`, `triggers` between specs |
| Archive loses change graph | `superseded_by` edge is permanent |
| No query capability | `query.py` for impact analysis, contract verification |
| No lint/validation | `spec-lint.py` with 5 automated rules |

## Key Design Decisions

### 1. Change nodes are graph citizens, not folders

OpenSpec puts changes in folders. We make them nodes with edges:
- `add-2fa → change_for → auth-spec` (which spec is being modified)
- `add-2fa → adds → 2fa-requirement` (what's new)
- `add-2fa → archives_to → auth-spec` (merged)

This preserves the change history as queryable edges forever.

### 2. Requirements are nodes, not markdown sections

OpenSpec puts requirements as ### sections in a single spec.md. We make each requirement a separate node with its own scenarios, guarantees, and test edges. This makes requirements individually queryable — "show me all requirements that depend on the User model."

### 3. Scenarios are nodes, not paragraphs

Each Given-When-Then scenario is a node linked to its requirement via `scenario_for`. This makes scenarios queryable and verifiable — lint can check that every requirement has at least one scenario.

### 4. The predicate vocabulary formalizes OpenSpec's natural language

Instead of "The system SHALL issue a JWT token," we have:
```
user-auth (requirement)
  ├── guarantees → secure_credential_storage
  ├── scenario_for → valid-login
  └── scenario_for → invalid-login
```

## Predicate Mapping: OpenSpec Concepts → Our Graph

| OpenSpec Concept | Our Predicate | Direction |
|-----------------|---------------|-----------|
| Spec describes component | `spec_of` | spec → component |
| Requirement in spec | `contains` | spec → requirement |
| Scenario for requirement | `scenario_for` | scenario → requirement |
| Change targets spec | `change_for` | change → spec |
| ADDED requirement | `adds` | change → requirement |
| MODIFIED requirement | `modifies` | change → requirement |
| REMOVED requirement | `removes` | change → requirement |
| Archive/merge | `archives_to` | change → spec |
| Given-When-Then | embedded in scenario node body | — |
| RFC 2119 (SHALL/MUST) | `strength: SHALL` in frontmatter | — |

## The Archive Edge Chain (Our Innovation)

OpenSpec loses the change graph on archive. We preserve it:

```
auth-spec (v3) ←──superseded_by── add-2fa
auth-spec (v2) ←──superseded_by── add-oauth
auth-spec (v1) ←──superseded_by── initial-auth
```

Query: "Why does auth-spec have 2FA?" → follow `superseded_by` → `add-2fa` → read proposal, design, tasks. Complete audit trail.

## NebulaGraph Upgrade Path

OpenSpec is file-based. We're graph-based. For large-scale spec graphs, we can sync to NebulaGraph (Apache 2.0) for:
- OpenCypher queries across all specs
- Interactive visualization (NebulaGraph Studio)
- Graph algorithms (PageRank for critical specs, community detection for coupling)

See `knowledge-graph: references/nebulagraph-integration.md` for setup.
