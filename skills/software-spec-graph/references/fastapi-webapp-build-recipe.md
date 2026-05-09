# FastAPI Web App Build Recipe

How to translate a spec graph into a running FastAPI + SQLAlchemy + React single-page application. Covers the implementation-side (Phase 7) of the spec-graph lifecycle for web apps.

## Architecture Pattern: Dual-Mode Graph

```
markdown files (source of truth)
        │
        ▼    sync engine (incremental)
SQLAlchemy DB (fast query layer)
        │
        ▼    FastAPI REST
React SPA
```

## Layer 1: Data Models (no dependencies)

### Model Design

Use three tables: `nodes` (polymorphic), `edges` (typed directed), `sync_runs` (audit).

```python
class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, index=True)
    kind = Column(String(50), nullable=False, index=True)  # discriminator
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=True)
    meta_json = Column(Text, nullable=True, default="{}")  # NOT 'metadata'!
    tags = Column(Text, nullable=True, default="[]")
    strength = Column(String(20), nullable=True)  # SHALL/MUST/SHOULD
    status = Column(String(50), nullable=True)    # proposed/completed
    source_file = Column(String(500), nullable=True)
    source_mtime = Column(Float, nullable=True)
    created_at = Column(DateTime, default=...)
    updated_at = Column(DateTime, default=..., onupdate=...)

class Edge(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    to_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    predicate = Column(String(100), nullable=False)
    properties = Column(Text, nullable=True, default="{}")
    __table_args__ = (
        UniqueConstraint("from_node_id", "predicate", "to_node_id"),
        Index("idx_edges_from_predicate", "from_node_id", "predicate"),
        Index("idx_edges_to_predicate", "to_node_id", "predicate"),
    )

class SyncRun(Base):
    __tablename__ = "sync_runs"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20))  # running/completed/failed
    nodes_created = Column(Integer, default=0)
    nodes_updated = Column(Integer, default=0)
    nodes_deleted = Column(Integer, default=0)
    edges_created = Column(Integer, default=0)
    edges_removed = Column(Integer, default=0)
```

### Gotchas

- **`metadata` is reserved** by SQLAlchemy's `Base.metadata`. Name your JSON column `meta_json` instead.
- **PEP 604 not available on Python 3.9**. Do NOT use `-> Node | None` return annotations. Remove them or use `Optional[Node]`.
- **SQLite pragmas**: enable WAL mode + foreign keys on connect for concurrent read performance.
- **Tags as JSON string**: SQLite has no native JSON array type; store tags as a JSON-encoded string column and parse when reading.

## Layer 2: Sync Engine

### Algorithm

```
1. Walk KNOWLEDGE_PATH, collect all .md files (skip queries/, scripts/, templates/)
2. For each file:
   a. Compare source_mtime with stored value → skip if unchanged (incremental)
   b. Read file content
   c. Parse YAML frontmatter (--- ... ---)
   d. Derive: slug from filename, kind from directory or frontmatter
   e. Parse |rel:PREDICATE| [[KIND/SLUG]] edges from body
   f. Deduplicate edges (set of tuples)
   g. Upsert node in DB
   h. DELETE all edges WHERE from_node_id = node.id
   i. INSERT all currently-parsed edges
3. Detect deleted files: nodes with source_file not in current file list → DELETE
4. Log sync_run with summary counts
```

### Edge Reconciliation Strategy

**Full replace per node** (not diffing):
- Delete all outgoing edges for the node
- Insert all currently parsed edges
- Simple, correct, handles additions, removals, and modifications equally

### Error Tolerance

- Malformed YAML → log, skip file, continue
- Missing kind: → infer from directory name (`specs/` → `spec`)
- Missing title: → auto-generate from slug (`hello-world` → `Hello World`)
- Broken edge target → create placeholder `reference` node, emit warning
- Circular edge (self-reference) → skip, log warning
- Deduplicate edges before insert to avoid UNIQUE constraint violations

### Kind Normalization

Some files set `kind: concepts` (plural) in frontmatter while the directory `concepts/` infers `concept` (singular). Normalize plurals to singular after reading kind from frontmatter:

```python
KIND_NORMALIZE = {
    "specs": "spec", "requirements": "requirement", "scenarios": "scenario",
    "changes": "change", "concepts": "concept", "tasks": "task",
    "tools": "tool", "people": "person", "organizations": "organization",
    "references": "reference", "projects": "project",
}
kind = KIND_NORMALIZE.get(kind, kind)
```

## Layer 3: FastAPI API

### Endpoint Design

| Endpoint | Purpose | Key Query Params |
|----------|---------|------------------|
| `GET /api/nodes` | List nodes | `?kind=spec,req&search=term&tag=security&page=1&page_size=50` |
| `GET /api/nodes/{slug}` | Node detail | — |
| `GET /api/edges` | List edges | `?predicate=contains&from_slug=X&to_slug=Y` |
| `POST /api/query/traverse` | BFS traversal | `{"seed": "...", "depth": 3, "direction": "forward"}` |
| `POST /api/query/path` | Shortest path | `{"from": "...", "to": "...", "max_depth": 10}` |
| `POST /api/sync` | Trigger sync | `{"force": false}` |
| `GET /api/stats` | Dashboard counts | — |

### Graph Traversal Implementation

BFS is implemented iteratively, not recursively, to avoid Python stack limits:

```python
def bfs_traverse(db, seed_id, depth, predicates, direction):
    visited = {seed_id}
    frontier = {seed_id}
    edges = []
    d = 0
    while frontier and d < depth:
        d += 1
        next_frontier = set()
        for node_id in frontier:
            q = db.query(Edge).filter(Edge.from_node_id == node_id)
            if predicates:
                q = q.filter(Edge.predicate.in_(predicates))
            for edge in q.all():
                if edge.to_node_id not in visited:
                    visited.add(edge.to_node_id)
                    next_frontier.add(edge.to_node_id)
                edges.append(edge)
        frontier = next_frontier
    return db.query(Node).filter(Node.id.in_(visited)).all(), edges
```

### Response Envelope

Standardize on `{"data": ..., "meta": {"total": N, "page": P, "page_size": S}}`

## Layer 4: React Frontend

### Views

| Route | Component | API Calls |
|-------|-----------|-----------|
| `/` | Dashboard | `GET /api/stats` |
| `/nodes?kind=X&search=Y` | NodeBrowser | `GET /api/nodes?kind=&search=&tag=&page=` |
| `/nodes/:slug` | NodeDetail | `GET /api/nodes/{slug}` |

### Proxy Setup (Vite)

```js
// vite.config.js
server: {
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } }
}
```

### Dark Theme Starter

Use these CSS variables as a foundation matching the Dark Dashboard pattern:

```css
body {
  background: #0d1117;
  color: #c9d1d9;
}
.card {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
}
```

## Build Order (Dependency Chain)

```
Phase 7 Step 1: models.py ────── Verify: sqlite3 .schema
Phase 7 Step 2: sync.py ──────── Verify: run_sync → check DB counts
Phase 7 Step 3: main.py ──────── Verify: curl /api/stats
Phase 7 Step 4: React scaffold ─ Verify: browser renders dashboard
Phase 7 Step 5: Archive change ─ ingest.py archives_to
```

Each step is independently verifiable before the next starts. Never write two layers at once.

## Files Created in Spec Studio Session

```
~/mywork/spec-studio/
├── backend/
│   ├── database.py       # SQLAlchemy engine, session, init_db()
│   ├── models.py         # Node, Edge, SyncRun ORM
│   ├── sync.py           # run_sync() — markdown → DB
│   └── main.py           # FastAPI app, 7 routes
├── frontend/
│   ├── src/
│   │   ├── api.js        # fetch wrapper for all endpoints
│   │   ├── App.jsx       # Router + sidebar layout
│   │   ├── Dashboard.jsx # Stats overview + sync button
│   │   ├── NodeBrowser.jsx # Filterable, paginated node list
│   │   ├── NodeDetail.jsx  # Full node + edges sections
│   │   └── index.css     # Dark theme (1200+ lines)
│   └── vite.config.js    # Port 5173, proxy /api → :8000
└── spec_studio.db        # SQLite (286 nodes, 771 edges)
```
