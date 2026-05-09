---
name: knowledge-graph
description: Persistent knowledge graph built from markdown files with typed predicates. Stores facts as subject-predicate-object triples in linked md files with YAML frontmatter. Supports graph traversal queries, saved query patterns, and automatic ingestion from natural language.
version: 1.6.0
---

# Knowledge Graph

A persistent, queryable knowledge graph using markdown files as nodes and typed predicates as edges. Designed for agentic AI memory — every fact the user shares is decomposed into subject-predicate-object triples and stored in an interlinked graph.

## Architecture

```
KNOWLEDGE_PATH/
├── SCHEMA.md         # Predicate definitions, conventions
├── index.md          # All nodes with one-line descriptions
├── log.md            # Chronological change log
├── people/           # People nodes
├── organizations/    # Organization nodes
├── concepts/         # Concept/philosophy nodes
├── tools/            # Tool/technology nodes
├── projects/         # Project nodes
├── references/       # Source/reference nodes
├── queries/          # Saved query patterns
└── scripts/          # Reusable Python tools
    ├── graph.py      # Core graph: build, traverse, search
    ├── ingest.py     # CLI: add facts as triples
    ├── query.py      # CLI: query the graph
    └── lint.py       # CLI: health check
```

## Configuration

Set `KNOWLEDGE_PATH` in `~/.hermes/.env`:
```
KNOWLEDGE_PATH=/Users/koustubh/mywork/knowledge-graph
```

Default: `~/mywork/knowledge-graph`

## Universal Predicates (The Grammar)

Every fact the user shares maps to one of these predicate types:

| Category | Predicate | Direction | Meaning |
|----------|-----------|-----------|---------|
| Identity | `is_a` | sub → obj | "X is a type of Y" |
| Identity | `same_as` | sub ↔ obj | "X is also known as Y" |
| Identity | `portion_of` | sub → obj | "X is part of Y" |
| Belief | `follows` | sub → obj | "X practices/adheres to Y" |
| Belief | `values` | sub → obj | "X holds Y in high regard" |
| Belief | `rejects` | sub → obj | "X actively avoids Y" |
| Belief | `prefers` | sub → obj over target | "X prefers Y over Z" |
| Influence | `influences` | sub → obj | "X shapes Y" |
| Influence | `enables` | sub → obj | "X makes Y possible" |
| Influence | `blocks` | sub → obj | "X prevents Y" |
| Dependency | `depends_on` | sub → obj | "X needs Y" |
| Dependency | `uses` | sub → obj | "X employs Y as tool" |
| Dependency | `produces` | sub → obj | "X generates Y" |
| Dependency | `builds` | sub → obj | "X creates/develops Y" |
| Temporal | `precedes` | sub → obj | "X happens before Y" |
| Temporal | `supersedes` | sub → obj | "X replaces Y as authoritative" |
| Source | `attests` | sub → obj | "X confirms/teaches Y" |
| Source | `contradicts` | sub ↔ obj | "X and Y are inconsistent" |
| Source | `teaches` | sub → obj | "X instructs Y" |
| Goal | `goals_for` | sub → obj | "X desires Y" |
| Goal | `constrains` | sub → obj | "X limits Y" |

For the full predicate grammar including software specification predicates (exposes, accepts, returns, triggers, fails_with, spec_of, scenario_for, change_for, adds, modifies, removes, archives_to, tests, guarantees, implements, conforms_to), see `~/mywork/knowledge-graph/SCHEMA.md`.

## Node File Format

Every node file has YAML frontmatter and bidirectional edges:

```markdown
---
title: Koustubh
kind: person
created: 2026-05-08
updated: 2026-05-08
tags: [user, systems-thinking, python-dev]
---
# Koustubh

|rel:follows| [[organizations/ramakrishna-mission]]
|rel:values| [[concepts/systems-thinking]]
|rel:values| [[concepts/free-open-source]]
|rel:uses| [[tools/python]]
|rel:goals_for| [[projects/escape-9-to-5]]
|rel:builds| [[projects/options-screener]]
|rel:builds| [[projects/reit-analyzer]]
|rel:influences| [[concepts/vedanta]]
```

**Edge format:** `|rel:PREDICATE| [[KIND/SLUG]]` (one per line)

**Reverse edge:** The ingest script automatically adds the inverse edge. Inverse mappings defined in the script's INVERSE_MAP.

## Script Usage

### 1. Ingest a fact

```bash
python3 scripts/ingest.py <subject> <predicate> <object> [--object-kind K] [--tags TAGS]

# Examples:
python3 scripts/ingest.py koustubh follows ramakrishna-mission --object-kind organizations
python3 scripts/ingest.py koustubh values systems-thinking --object-kind concepts
python3 scripts/ingest.py vedanta influences swami-vivekananda --object-kind people
python3 scripts/ingest.py koustubh prefers sqlite --over grafana --object-kind tools
```

This:
- Creates or updates the subject's node file with the forward edge
- Creates or updates the object's node file with the reverse edge
- Updates index.md and log.md

**IMPORTANT:** Always use plural kind names: `--object-kind concepts`, `--object-kind projects`, `--object-kind people`, `--object-kind organizations`, `--object-kind tools`, `--object-kind references`. See Implementation Gotcha #8.

### 2. Query the graph

```bash
# Find all nodes connected to a seed within N hops
python3 scripts/query.py "koustubh" --depth 2

# Find a path between two nodes
python3 scripts/query.py --path "vedanta" "options-screener"

# Find all nodes of a kind related to a seed via a predicate
python3 scripts/query.py "koustubh" --via follows --of-kind organization

# Subgraph — everything connected to a concept
python3 scripts/query.py "systems-thinking" --depth 3

# JSON output for programmatic use
python3 scripts/query.py "upanishads" --depth 1 --format json
```

Output: JSON with nodes (id, title, kind) and edges (source, target, predicate).

### 3. Lint and maintain

```bash
python3 scripts/lint.py
```

Reports:
- Orphan nodes (0 inbound links)
- Broken edges (link targets that don't exist)
- Contradictions (nodes connected by `contradicts`)
- Stale nodes (last updated > N days)
- Index completeness
- Incomplete frontmatter

### 4. Save a query pattern

After a useful query, save it:

```bash
python3 scripts/query.py "koustubh" --depth 2 --save "user-ecosystem"
```

Creates `queries/user-ecosystem.md` with the pattern.

## Agent Workflow

### When the user shares a fact

1. Parse the statement into subject-predicate-object
2. Check if subject node exists; create if not (infer `kind:` from context)
3. Check if object node exists; create if not (use `--object-kind` from context)
4. Run `ingest.py` to add the edge
5. If the fact creates an interesting connection, suggest saving a query

### When the user asks a question

1. Extract key entities and intent from the question
2. Find seed nodes via `search_files` across the knowledge directory
3. Choose the right graph operation (neighbors, path, subgraph, kind-filtered)
4. Run the appropriate `query.py` call
5. Synthesize the response from the returned subgraph
6. If the answer reveals new insight, optionally save as a query pattern

### When a conversation covers complex ground

1. Identify 3-10 facts from the conversation
2. Ingest them all as triples in batch (one call to ingest.py per triple)
3. Verify by running a query that should return the expected connections
4. Commit graph state

## Example: Query Results

Given the graph:

```
koustubh |follows| ramakrishna-mission
ramakrishna-mission |teaches| vedanta
vedanta |influences| swami-vivekananda
swami-vivekananda |influences| koustubh
koustubh |values| systems-thinking
systems-thinking |influences| options-screener
```

Query: `python3 scripts/query.py "koustubh" --depth 2`

Returns:
```json
{
  "nodes": [
    {"id": "people/koustubh", "title": "Koustubh", "kind": "person"},
    {"id": "organizations/ramakrishna-mission", "title": "Ramakrishna Mission", "kind": "organization"},
    {"id": "concepts/systems-thinking", "title": "Systems Thinking", "kind": "concept"},
    {"id": "concepts/vedanta", "title": "Vedanta", "kind": "concept"},
    {"id": "people/swami-vivekananda", "title": "Swami Vivekananda", "kind": "person"},
    {"id": "projects/options-screener", "title": "Options Screener", "kind": "project"}
  ],
  "edges": [
    {"source": "people/koustubh", "target": "organizations/ramakrishna-mission", "predicate": "follows"},
    {"source": "people/koustubh", "target": "concepts/systems-thinking", "predicate": "values"},
    {"source": "people/koustubh", "target": "concepts/vedanta", "predicate": "influences"},
    {"source": "organizations/ramakrishna-mission", "target": "concepts/vedanta", "predicate": "teaches"},
    {"source": "concepts/vedanta", "target": "people/swami-vivekananda", "predicate": "influences"},
    {"source": "people/swami-vivekananda", "target": "people/koustubh", "predicate": "influences"},
    {"source": "concepts/systems-thinking", "target": "projects/options-screener", "predicate": "influences"}
  ],
  "paths_from_seed": {
    "koustubh -> ramakrishna-mission -> vedanta -> swami-vivekananda": 3,
    "koustubh -> systems-thinking -> options-screener": 2
  }
}
```

## Implementation Gotchas (from real debugging)

These were discovered while building the graph and scripts — each one caused a real bug:

### 1. YAML parses dates as date objects, not strings
When `created: 2026-05-08` appears in frontmatter, `yaml.safe_load` returns a `datetime.date` object, not the string `"2026-05-08"`. This crashes `strptime` calls in lint and anywhere that expects string comparison.

**Fix in graph.py:** The `parse_frontmatter` function post-processes `created` and `updated` fields with `.isoformat()` if they're not strings. The `Node.__init__` also normalises incoming values.

### 2. Tag matches pollute seed node selection
`find_nodes("vedanta")` returned 4 nodes because `ramakrishna-mission` has a tag `vedanta`. When used to select seeds for `--path` queries, the wrong node was picked first (the `from_nodes[0]` assumption broke).

**Fix in graph.py:** `find_nodes` now returns results sorted by match quality: exact slug > slug substring > title match > tag match. The `--path` query picks `[0]` which is now the correct seed.

### 3. Argparse duplicate --depth definition
`query.py` defined `--depth` twice (once with other args, once at the bottom) — argparse raises `ArgumentError` on conflicting option strings.

**Fix:** Removed the duplicate definition.

### 4. Broken edges from obsolete references
A node `walk-forward-cv.md` had an edge `|rel:supersedes| [[concepts/backtest-overfitting]]` where `backtest-overfitting` didn't exist as a node. The lint script caught this as a broken edge.

**Lesson:** Always run `lint.py` after ingesting. If an edge references a node that doesn't exist, either create the node or remove the edge.

### 5. The `prefers` predicate needs an extra argument
`prefers` is the only ternary predicate — it compares two objects. The `ingest.py` script handles this with `--over TARGET`:

```bash
python3 scripts/ingest.py koustubh prefers sqlite --over grafana --object-kind tools
```

### 6. Python 3.9 `str | None` crashes ingest.py
`def find_node_file(root: str, slug: str) -> str | None:` uses PEP 604 union syntax (Python 3.10+). On macOS default Python 3.9.6, this raises `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`. **Fix:** remove the return type annotation entirely. Do NOT add `from __future__ import annotations` — PEP 604 is not backported by it.

### 7. Ingest.py used bare slugs instead of `kind/slug` in edge targets
The original code called `add_edge_to_file(subj_file, pred, obj_slug)` where `obj_slug` was just the bare name (e.g., `"factual-verification"`). But all existing edges use the `kind/slug` format (e.g., `[[concepts/factual-verification]]`). This caused broken edges because the graph parser derives slugs from file paths relative to root.

**Fix:** Compute `obj_full_slug = f"{obj_kind}/{obj_slug}"` and `subj_full_slug = f"{subj_kind}/{subj_slug}"`, then pass those to `add_edge_to_file` for both forward and reverse edges. Derive `obj_kind` and `subj_kind` from the actual directory name via `os.path.relpath(filepath, root).split(os.sep)[0]` — do NOT read the `kind` field from frontmatter, because frontmatter uses singular (`kind: person`) while directories are plural (`people/`). The earlier approach using `parse_frontmatter` was wrong for exactly this reason: it produced `concept/koustubh` instead of `people/koustubh`.

### 8. `--object-kind` must match existing directory plurals
The graph uses plural directory names: `concepts/`, `projects/`, `tools/`, `people/`, `organizations/`. Passing `--object-kind concept` (singular) creates files in `concept/` (singular), producing a parallel directory tree that `build_graph` doesn't scan. Always use the plural form: `--object-kind concepts`, `--object-kind projects`, etc.

### 9. Ingest after EVERY critical phase — don't batch at the end
The agent has a documented meta-failure: forgetting to ingest findings into the graph after clarify responses, exploration phases, code reviews, and build completions. The `EXPLORATION_GATE` and `GRAPH_UPDATE_CHECKPOINT` lint rules (in software-spec-graph) now enforce this. After every clarify response, immediately run `ingest.py` to capture the finding. The graph is the source of truth — it must reflect current state at all times.

### 10. SQLite schema evolution requires DB deletion during development
`CREATE TABLE IF NOT EXISTS` does not update columns on existing tables. When adding columns during development, delete the DB file (`rm candle_crm.db`) and let the app recreate it. For production, add migration logic. This is documented as the `sqlite-schema-evolution` reusable pattern.

### 11. YAML parses bare numbers in tags as integers
Tags like `[1893, chicago]` cause YAML to parse `1893` as an integer, which crashes `find_nodes` when it calls `.lower()` on tags. Quote numeric tags: `['1893', chicago]`. The `find_nodes` function now guards against this with `isinstance(tag, str)`, but quoting is still safer.

### 12. NebulaGraph: `change` is a reserved word in nGQL (from Implementation Gotcha above)
When syncing to NebulaGraph, `kind: change` nodes must map to the `delta` tag. The sync script handles this via `KIND_TO_TAG`. Markdown files keep `kind: change`. See `references/nebulagraph-integration.md` for full setup.

### 13. NebulaGraph: first-run ADD HOSTS required (from Implementation Gotcha above)
On fresh Docker deployment, storaged can't register with metad. The fix: temporarily remove storaged dependency from graphd, start, run `ADD HOSTS "storaged":9779` via nebula-console, restart storaged. Full sequence in `references/nebulagraph-integration.md`.

## NebulaGraph Backend

The knowledge graph can be synced to NebulaGraph (Apache 2.0) for Cypher queries, graph visualization, and code generation. Setup: `~/mywork/nebula/docker-compose.yaml`. Full integration guide: [references/nebulagraph-integration.md](references/nebulagraph-integration.md).

### 12. YAML parses unquoted numbers in tags as ints, crashing `find_nodes`
When tags like `--tags "1898"` are passed to ingest.py, the frontmatter gets `[1898]` (bare number, no quotes). YAML parses this as an `int`, and `find_nodes` calls `tag.lower()` on it — ints have no `.lower()`, causing `AttributeError`.

**Two-part fix:** (a) In graph.py's `find_nodes`, guard with `isinstance(tag, str)` before calling `.lower()`. (b) When creating nodes with numeric tags, quote them: `tags: [monastic,belur-math,'1898']`.

### 13. `references/` was excluded from `build_graph` and `lint`
Both `graph.py` and `lint.py` had `"references"` in their `skip_dirs` set, but the SCHEMA defines `reference` as a valid node kind. All reference nodes (texts, events, source documents) were invisible to queries and lint. **Fix:** remove `"references"` from `skip_dirs` in both files. Keep `"queries"`, `"scripts"`, and `"templates"` — those are meta directories.

### 14. `--title` flag applies to the OBJECT node, not the subject
When ingesting a fact with two new nodes (e.g., `nachiketa follows yama --title "Nachiketa"`), `--title` is applied to the OBJECT (`yama`), not the subject. This gave Yama the title "Nachiketa". The subject's title is always auto-generated from its slug.

**Rule:** When both subject and object are new nodes with different names, do NOT use `--title`. Let both auto-generate from slugs. If both need custom titles, create the subject node first via a separate ingest, then make the real relationship call where `--title` targets the object safely.

### 15. NebulaGraph sync: `task` kind needs `tasks` plural in KIND_TO_TAG

The sync script's `KIND_TO_TAG` dict maps markdown kind names to NebulaGraph tags. When ingest.py creates nodes with `--object-kind tasks` (plural), the markdown frontmatter gets `kind: tasks`. But the sync script only mapped `task: task` (singular). All `kind: tasks` nodes were silently dropped during sync because no tag matched.

**Fix:** Add both singular and plural forms: `"task": "task", "tasks": "task"`. Apply to all kinds: `"change": "delta", "changes": "delta"`, `"requirement": "requirement", "requirements": "requirement"`, etc.

### 16. NebulaGraph sync: edge types must exist before syncing edges

NebulaGraph rejects `INSERT EDGE` for edge types not yet created. The sync script inserts all vertices first, then all edges. If an edge type (e.g., `touches`) was created AFTER vertices were synced, the edge insertion silently fails.

**Fix:** Always run `nebula_init.py` before `sync_markdown_to_nebula.py`. When adding new predicates to INVERSE_MAP, also create the corresponding edge type in NebulaGraph: `CREATE EDGE IF NOT EXISTS touches(description STRING);`.

### 17. NebulaGraph: `ADD HOSTS` required on first startup (see also #13 above)

On a fresh NebulaGraph Docker deployment, storaged cannot heartbeat to metad until `ADD HOSTS` is run through graphd. This creates a chicken-and-egg problem: storaged won't become healthy until registered, graphd won't start until storaged is healthy.

**Fix sequence:**
1. Temporarily remove `depends_on: storaged` from graphd in docker-compose
2. Start all services
3. Run `ADD HOSTS "storaged":9779` through nebula-console connected to graphd:9669
4. Restart storaged — now it registers successfully
5. Restore storaged dependency for future restarts

The `--local_config=true` flag works for storaged/graphd but NOT for metad (crashes with "unknown command line flag").

- **Don't fragment nodes** — one node per entity. "RAM" and "Random Access Memory" should be `same_as`, not two nodes
- **Bidirectional consistency** — always add reverse edges in the same transaction
- **Predicate vocab is not user-configurable by default** — adding new predicates requires updating SCHEMA.md AND the INVERSE_MAP in graph.py. This is intentional — it prevents predicate drift
- **Depth limits** — queries beyond depth 4 on 500+ node graphs can be slow. Default max depth: 4
- **Node naming** — use lower-kebab-case slugs. `swami-vivekananda`, `ramakrishna-mission`, `systems-thinking`
- **File renames break edges** — if a node file is renamed, all `|rel:|` links to it break. Use lint.py after renames
- **Don't store ephemeral data** — conversation state, in-progress work, session IDs. This is durable long-term memory
- **Don't collapse rich directives into bullets** — when migrating from memory to graph, keep full descriptive text in the node body. A concise bullet point like "systems thinking — interconnected parts" is not equivalent to the full directive. The node body (after frontmatter) is where rich content lives.
- **Always run lint.py after bulk operations** — it catches broken edges, missing index entries, and orphans
- **Set `updated:` manually after editing** — the scripts update frontmatter dates automatically on edge addition, but manual body edits need manual date bumps
- **nGQL reserves `change` as a keyword** — NebulaGraph rejects `CREATE TAG change`. Use `delta` as the tag name in NebulaGraph for change nodes, while keeping `kind: change` in markdown files. The sync script's KIND_TO_TAG mapping handles this automatically. See `references/nebulagraph-integration.md`.

### 15. Edge deduplication required — |rel:| lines may repeat in a file
A single markdown file may contain the same `|rel:|` line twice (copy-paste artifact, manual editing mistake). When a sync engine parses edges and inserts them into a relational DB with a UNIQUE constraint on `(from_node_id, predicate, to_node_id)`, the second occurrence fires an IntegrityError.

**Fix in sync engines:** Always deduplicate parsed edges before insertion. Use a `seen` set:
```python
def parse_edges(body):
    edges = []
    seen = set()
    for match in EDGE_RE.finditer(body):
        key = (match.group(1), match.group(2), match.group(3))
        if key not in seen:
            seen.add(key)
            edges.append(key)
    return edges
```

### 16. Frontmatter `kind:` may use plural forms (concepts vs concept)
The knowledge graph directories are plural (`concepts/`, `specs/`, `requirements/`, `changes/`). But some markdown files have `kind: concepts` (plural) in their YAML frontmatter while the directory name implies `concept` (singular). When a sync engine reads `kind` from frontmatter, it may produce inconsistent kind values.

**Fix:** After reading `kind` from frontmatter, normalize plurals to singular:
```python
KIND_NORMALIZE = {
    "specs": "spec", "requirements": "requirement", "scenarios": "scenario",
    "changes": "change", "concepts": "concept", "tasks": "task",
    "tools": "tool", "people": "person", "organizations": "organization",
    "references": "reference", "projects": "project",
}
kind = KIND_NORMALIZE.get(kind, kind)
```

This normalization must happen BEFORE the node is upserted.

### 17. `contains` predicate works for spec→spec AND spec→requirement
The `contains` predicate is overloaded: it links a platform spec to its sub-specs (spec→spec) AND links a spec to its requirements (spec→requirement). Both are valid and co-exist.

When querying, use `--depth` to control how far:
```bash
# Just sub-specs
python3 query.py "platform" --via contains --depth 1

# All requirements within sub-specs
python3 query.py "platform" --via contains --depth 3
```

## References

- [Domain Modeling](references/domain-modeling.md) — The 4-phase pattern for building rich, queryable subgraphs. Spine-first, layered predicates, hero query. Drawn from the 66-node Vedanta lineage build.
- [NebulaGraph Cleanup](references/nebulagraph-cleanup.md) — How to drop and recreate the NebulaGraph space when content is removed from the markdown source. Required after stripping personal data for a public repo.
