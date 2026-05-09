# Spec Studio — Complete Lifecycle Worked Example

This document captures the full spec-graph lifecycle applied to the Spec Studio project (May 2026). It serves as a concrete reference for how to move from a vague requirement ("build a web app") through Phases 0–7 to a complete, linted specification graph.

## Requirement

> "I want to build a web application using the software-spec-graph methodology. SQLAlchemy data models are core. Content/Knowledge domain. A tool that generates/manages spec graphs."

## Phase 0: Requirement Intake (5 clarify questions)

The agent asked 5 probing questions instead of jumping to specs:

| Question | Answer | Constraint Captured |
|----------|--------|---------------------|
| What domain? | Content/Knowledge — spec graph management | — |
| Core idea? | A tool that generates/manages spec graphs | — |
| Frontend stack? | FastAPI backend + SPA frontend | — |
| MVP feature? | Dashboard to view/query existing graph nodes | — |
| Data model? | Dual: markdown source of truth, SQLAlchemy for fast queries | — |

**Key pattern:** Each answer was immediately ingested into the knowledge graph. Do not batch findings at the end.

## Phase 0.5: Graph Inventory

Queried existing reusable patterns:

```bash
cd ~/mywork/knowledge-graph
KNOWLEDGE_PATH=~/mywork/knowledge-graph \
  python3 ~/.hermes/skills/research/knowledge-graph/scripts/query.py "reusable" --depth 1
```

**Found 12 reusable patterns**, including: `Fastapi Sqlite Crud`, `Dark Dashboard`, `Dashboard As Triage`, `Neo Brutalist Css`, `Sqlite Schema Evolution`, `Spec Driven Workflow`.

These were linked via `reuses` edges on the platform spec.

## Phase 1: PROPOSE — Decompose

Created exploration change node and decomposed into 8 sub-problems:

```bash
python3 scripts/ingest.py "explore-spec-studio" "change_for" "spec-studio-platform" \
  --subject-kind changes --object-kind specs

# Each sub-problem as a concept node
python3 scripts/ingest.py "explore-spec-studio" "adds" "graph-sync-engine" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "view-query-dashboard" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "typed-node-schema" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "predicate-edge-schema" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "spa-frontend" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "api-layer" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "spec-graph-visualization" --subject-kind changes --object-kind concepts
python3 scripts/ingest.py "explore-spec-studio" "adds" "query-engine" --subject-kind changes --object-kind concepts
```

## Phases 2–3: Explore & Decide

Evaluated frontend frameworks (React vs Svelte vs Vue). Chose React ("biggest ecosystem, shadcn/ui for fast building"). Ingested into exploration node by editing its tags.

## Phase 4: SPECIFY — Write 4 Specs + 19 Requirements + 4 Scenarios

### Spec Structure

```
spec-studio-platform (top-level)
├── contains → data-model-spec
├── contains → sync-engine-spec
├── contains → api-layer-spec
├── contains → dashboard-spec
└── reuses → [Fastapi Sqlite Crud, Dark Dashboard, ...]
```

### Data Model Spec (the core)

Key design: single `nodes` table (polymorphic via `kind` discriminator), single `edges` table (from_node → to_node + predicate + properties JSON). `source_file` + `source_mtime` for incremental sync. `sync_runs` table for audit trail.

Requirements: `polymorphic-nodes` [SHALL], `typed-directed-edges` [SHALL], `graph-traversal-indexes` [SHALL], `sync-compatibility` [SHALL], `source-traceability` [SHOULD].

### API Layer Spec (with contracts)

7 endpoints exposed via `exposes` predicate:
- `GET /api/nodes` — list + filter + paginate
- `GET /api/nodes/{slug}` — detail with edges
- `GET /api/edges` — list edges by predicate
- `POST /api/query/traverse` — BFS traversal from seed
- `POST /api/query/path` — shortest path between nodes
- `POST /api/sync` — trigger markdown sync
- `GET /api/stats` — dashboard summary

### Sync Engine Spec

Algorithm: walk files → check mtime → parse YAML + |rel:| edges → upsert nodes → full-replace edges (delete stale, insert new) → detect deleted files.

### Dashboard Spec (React SPA)

5 views: `/` (overview), `/nodes` (browser), `/nodes/:slug` (detail), `/explore` (graph viz), sync panel widget.

## Phase 5: Lint — Run spec-lint.py

23 issues found:
- 15 SCENARIO_FOR_REQ (expected at spec stage — prioritized 4 critical scenarios)
- 2 GUARANTEES_HAS_TESTS (tests come in Phase 7)
- 1 DEPLOYMENT_SPECIFIED (fixed by adding `deploys_to localhost-dev-server`)
- 5 AUTH_SPECIFIED (intentional — local tool, no auth for MVP)

**Bug discovered during lint:** `check_consistent_fallbacks` in `spec-lint.py` had `any(e.source == ...)` without a `for e in g.edges` clause. The variable `e` was never bound, making the generator expression always produce an empty iterator and the rule silently pass. Fixed by adding `for edge in g.edges`.

## Result: 31 nodes, 48 edges

```bash
python3 scripts/query.py "spec-studio-platform" --depth 2
```

Shows the complete graph: 4 specs, 19 requirements, 4 scenarios, 7 endpoint concepts, 4 reusable pattern links.

## Key Takeaways

1. **Start with clarify questions** — 5 questions revealed the tech stack, MVP focus, data model approach, and framework choice. Never spec from a single line.
2. **Ingest findings immediately** — after each clarify answer, run `ingest.py`. Don't batch.
3. **Query reusable inventory first** — Phase 0.5 discovered 12 patterns, 4 were directly reusable.
4. **Contains works for spec→spec** — hierarchical specs use the same `contains` predicate as spec→requirement.
5. **Lint early, lint often** — caught the missing deploy target and a script bug before any code was written.
6. **Progressive rigor** — not every requirement needs a scenario at spec stage. Add scenarios for the most critical ones, fill the rest before implementation.
