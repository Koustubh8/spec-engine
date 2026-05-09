# The 8-Phase Spec Lifecycle

The full lifecycle for spec-driven development. Do NOT skip Phases 0-3 — exploration before specification is where the value lives.

## Phase 0: Requirement Intake

A single line of requirement arrives. Do NOT immediately write specs. This is raw material for exploration.

**Critical: Involve the user before building anything.** Ask 5-7 probing questions about workflow, pain points, volume, constraints, and existing tools. Every answer becomes a concept node in the exploration graph with a `constrains` edge.

```bash
# After each answer, immediately ingest into the graph
python3 ingest.py "answer" "constrains" "sub-problem" --subject-kind concepts --object-kind concepts
```

## Phase 0.5: Graph Inventory

**Before proposing any new spec, query what already exists.** Query the knowledge graph for reusable patterns, existing specs, and working implementations.

```bash
python3 query.py "reusable" --depth 1
python3 query.py "auth-spec" --depth 2 --via exposes,contains
```

Every new spec should have `reuses` edges to the patterns it leverages.

## Phase 1: Propose — Decompose

Create an exploration change node and break the requirement into sub-problems.

```bash
python3 ingest.py "explore-project" "change_for" "project-spec" --subject-kind changes --object-kind specs

# Decompose: one adds edge per sub-problem (typically 5-10)
python3 ingest.py "explore-project" "adds" "sub-problem-1" --subject-kind changes --object-kind concepts
```

## Phase 2: Explore — Analyze Constraints

For each sub-problem, identify constraints (hard limits), risks (things that might fail), and unknowns (things to learn). Each becomes a concept node with a `constrains` edge.

```bash
python3 ingest.py "constraint" "constrains" "sub-problem" --subject-kind concepts --object-kind concepts
```

**Lint check:** Every sub-problem should have at least one `constrains` edge.

## Phase 3: Decide — Architecture with Rationale

Enumerate architecture options. Mark chosen vs rejected with explicit rationale using the `supersedes` + `blocks` + `enables` triad.

```bash
python3 ingest.py "explore-project" "adds" "option-a" --subject-kind changes --object-kind concepts
python3 ingest.py "option-a" "supersedes" "option-b" --subject-kind concepts --object-kind concepts
python3 ingest.py "option-b" "blocks" "core-requirement" --subject-kind concepts --object-kind concepts
python3 ingest.py "option-a" "enables" "project-spec" --subject-kind concepts --object-kind specs
```

Future agents reading the graph will see what was rejected and why.

## Phase 4: Specify — Requirements and Scenarios

Write spec nodes, requirement nodes (SHALL/MUST/SHOULD), and scenario nodes (Given-When-Then).

```bash
# Create spec
python3 ingest.py "new-spec" "spec_of" "component" --subject-kind specs --object-kind tools

# Add requirements
python3 ingest.py "new-spec" "contains" "requirement-1" --subject-kind specs --object-kind requirements

# Add scenarios
python3 ingest.py "scenario-1" "scenario_for" "requirement-1" --subject-kind scenarios --object-kind requirements
```

Use templates from `templates/` for file structure.

## Phase 5: Lint — Verify Completeness

Run ALL lint rules before implementation:

```bash
python3 tools/spec-studio/backend/spec-lint.py   # 14 spec rules
python3 tools/spec-studio/backend/prod_lint.py    # 12 production rules
```

| Severity | Action |
|----------|--------|
| ERROR | Fix before proceeding — missing contracts |
| WARNING | Fix or document exception — missing scenarios |

When a lint rule fires, treat it as a spec gap — add the missing edge/node.

## Phase 6: Impact Analysis

Before implementing, understand blast radius:

```bash
python3 query.py "spec" --depth 3 --via depends_on,triggers,implements
python3 query.py "spec" --via exposes --depth 2
python3 query.py --path "requirement-a" "test-b"
```

## Phase 7: Implement

Read the subgraph and generate code. For each requirement in the spec:
- Each scenario → test (Given-When-Then → pytest)
- Exposed endpoints → route handlers (from `exposes` edges)
- Input validation → from `accepts` schema edges
- Error responses → from `fails_with` edges

## Phase 8: Archive

Archive the change to preserve history permanently:

```bash
python3 ingest.py "change" "archives_to" "spec" --subject-kind changes --object-kind specs
```

The `superseded_by` chain is permanent. You can always trace: "Why does this spec have feature X?" → follow the edge back to the change proposal.
