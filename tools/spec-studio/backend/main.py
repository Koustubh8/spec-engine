"""
FastAPI application — Spec Studio API.

api-layer-spec:
  - restful-endpoints [SHALL]: 7 REST endpoints with Pydantic models
  - pagination-and-filtering [SHALL]: offset pagination, kind/search/tag filters
  - graph-traversal-api [SHALL]: BFS traversal with seed+depth
  - sync-trigger [SHALL]: POST /api/sync
  - stats-summary [SHALL]: GET /api/stats
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.orm import Session

# Ensure backend/ is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db, init_db, engine
from models import Node, Edge, SyncRun, VALID_NODE_KINDS
from sync import run_sync
from prod_lint import run_prod_lint


app = FastAPI(title="Spec Studio", version="0.1.0", docs_url="/docs")

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── PYDANTIC MODELS ──────────────────────────────────────────────────────────

class NodeOut(BaseModel):
    id: int
    slug: str
    kind: str
    title: str
    body: Optional[str] = None
    tags: list = []
    strength: Optional[str] = None
    status: Optional[str] = None
    source_file: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class NodeDetailOut(NodeOut):
    outgoing_edges: list = []
    incoming_edges: list = []


class EdgeOut(BaseModel):
    id: int
    from_node_id: int
    to_node_id: int
    predicate: str
    properties: dict = {}
    from_slug: Optional[str] = None
    from_title: Optional[str] = None
    from_kind: Optional[str] = None
    to_slug: Optional[str] = None
    to_title: Optional[str] = None
    to_kind: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class Meta(BaseModel):
    total: int
    page: int
    page_size: int


class ListResponse(BaseModel):
    data: list
    meta: Meta


class TraverseRequest(BaseModel):
    seed: str
    depth: int = 3
    predicates: Optional[list[str]] = None
    direction: str = "forward"  # forward | reverse | both


class PathRequest(BaseModel):
    from_node: str = Query(..., alias="from")
    to_node: str = Query(..., alias="to")
    max_depth: int = 10


class SyncRequest(BaseModel):
    force: bool = False


class SyncOut(BaseModel):
    status: str
    summary: Optional[dict] = None


class StatsOut(BaseModel):
    total_nodes: int
    total_edges: int
    by_kind: dict
    top_predicates: list
    by_tag: dict
    last_sync: Optional[dict] = None


# ─── LIFECYCLE ────────────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    """Create tables on first run."""
    init_db()


# ─── NODES ENDPOINTS ──────────────────────────────────────────────────────────

@app.get("/api/nodes", response_model=ListResponse)
def list_nodes(
    kind: Optional[str] = Query(None, description="Comma-separated kinds"),
    search: Optional[str] = Query(None, description="Search title and body"),
    tag: Optional[str] = Query(None, description="Filter by exact tag"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET /api/nodes — List nodes with filtering and pagination."""
    q = db.query(Node)

    # Kind filter
    if kind:
        kinds = [k.strip() for k in kind.split(",") if k.strip()]
        q = q.filter(Node.kind.in_(kinds))

    # Search filter (LIKE on title and body)
    if search:
        like = f"%{search}%"
        q = q.filter(
            Node.title.ilike(like) | Node.body.ilike(like)
        )

    # Tag filter (JSON array contains)
    if tag:
        like_tag = f"%{tag}%"
        q = q.filter(Node.tags.ilike(like_tag))

    total = q.count()
    nodes = q.order_by(Node.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [n.to_dict(include_edges=False) for n in nodes],
        "meta": {"total": total, "page": page, "page_size": page_size},
    }


@app.get("/api/nodes/{slug}", response_model=NodeDetailOut)
def get_node(slug: str, db: Session = Depends(get_db)):
    """GET /api/nodes/{slug} — Single node with edges."""
    node = db.query(Node).filter(Node.slug == slug).first()
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{slug}' not found")
    return node.to_dict(include_edges=True)


# ─── EDGES ENDPOINT ───────────────────────────────────────────────────────────

@app.get("/api/edges", response_model=ListResponse)
def list_edges(
    predicate: Optional[str] = Query(None),
    from_slug: Optional[str] = Query(None),
    to_slug: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """GET /api/edges — List edges with filtering."""
    q = db.query(Edge)

    if predicate:
        q = q.filter(Edge.predicate == predicate)

    if from_slug:
        from_node = db.query(Node).filter(Node.slug == from_slug).first()
        if from_node:
            q = q.filter(Edge.from_node_id == from_node.id)
        else:
            return {"data": [], "meta": {"total": 0, "page": page, "page_size": page_size}}

    if to_slug:
        to_node = db.query(Node).filter(Node.slug == to_slug).first()
        if to_node:
            q = q.filter(Edge.to_node_id == to_node.id)
        else:
            return {"data": [], "meta": {"total": 0, "page": page, "page_size": page_size}}

    total = q.count()
    edges = q.order_by(Edge.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Eagerly load related nodes
    node_ids = set()
    for e in edges:
        node_ids.add(e.from_node_id)
        node_ids.add(e.to_node_id)
    nodes = {n.id: n for n in db.query(Node).filter(Node.id.in_(node_ids)).all()}
    for e in edges:
        e.source_node = nodes.get(e.from_node_id)
        e.target_node = nodes.get(e.to_node_id)

    return {
        "data": [e.to_dict_with_nodes() for e in edges],
        "meta": {"total": total, "page": page, "page_size": page_size},
    }


# ─── GRAPH TRAVERSAL ──────────────────────────────────────────────────────────

def bfs_traverse(db: Session, seed_id: int, depth: int,
                 predicates: Optional[list[str]], direction: str):
    """Iterative BFS traversal. Returns (nodes, edges)."""
    visited_node_ids = {seed_id}
    frontier = {seed_id}
    discovered_edges = []
    current_depth = 0

    while frontier and current_depth < depth:
        current_depth += 1
        next_frontier = set()

        for node_id in frontier:
            # Forward edges
            if direction in ("forward", "both"):
                q = db.query(Edge).filter(Edge.from_node_id == node_id)
                if predicates:
                    q = q.filter(Edge.predicate.in_(predicates))
                for edge in q.all():
                    if edge.to_node_id not in visited_node_ids:
                        next_frontier.add(edge.to_node_id)
                        visited_node_ids.add(edge.to_node_id)
                    discovered_edges.append(edge)

            # Reverse edges
            if direction in ("reverse", "both"):
                q = db.query(Edge).filter(Edge.to_node_id == node_id)
                if predicates:
                    q = q.filter(Edge.predicate.in_(predicates))
                for edge in q.all():
                    if edge.from_node_id not in visited_node_ids:
                        next_frontier.add(edge.from_node_id)
                        visited_node_ids.add(edge.from_node_id)
                    discovered_edges.append(edge)

        frontier = next_frontier

    # Fetch all nodes
    nodes = db.query(Node).filter(Node.id.in_(visited_node_ids)).all()
    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in discovered_edges:
        key = (e.from_node_id, e.predicate, e.to_node_id)
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return nodes, unique_edges


@app.post("/api/query/traverse")
def traverse_graph(req: TraverseRequest, db: Session = Depends(get_db)):
    """POST /api/query/traverse — BFS traversal from seed."""
    seed = db.query(Node).filter(Node.slug == req.seed).first()
    if not seed:
        raise HTTPException(status_code=404, detail=f"Seed node '{req.seed}' not found")

    nodes, edges = bfs_traverse(db, seed.id, req.depth, req.predicates, req.direction)

    # Build path summary
    root_id = seed.id
    path_hops = {}
    for e in edges:
        if e.from_node_id == root_id:
            path_hops[f"{seed.slug} -> {e.target_node.slug if e.target_node else e.to_node_id}"] = 1
        if e.to_node_id == root_id:
            path_hops[f"{e.source_node.slug if e.source_node else e.from_node_id} -> {seed.slug}"] = 1

    return {
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict_with_nodes() for e in edges],
        "paths_from_seed": path_hops,
    }


@app.post("/api/query/path")
def find_path(req: PathRequest, db: Session = Depends(get_db)):
    """POST /api/query/path — Shortest path between two nodes (BFS)."""
    from_node = db.query(Node).filter(Node.slug == req.from_node).first()
    to_node = db.query(Node).filter(Node.slug == req.to_node).first()

    if not from_node:
        raise HTTPException(status_code=404, detail=f"Node '{req.from_node}' not found")
    if not to_node:
        raise HTTPException(status_code=404, detail=f"Node '{req.to_node}' not found")

    if from_node.id == to_node.id:
        return {"found": True, "path": [{"node": from_node.to_dict(), "edge": None}], "hops": 0}

    # BFS path finding
    visited = {from_node.id: (None, None)}  # node_id -> (parent_id, edge)
    frontier = [from_node.id]
    found = False

    while frontier and not found:
        next_frontier = []
        for node_id in frontier:
            for edge in db.query(Edge).filter(
                (Edge.from_node_id == node_id) | (Edge.to_node_id == node_id)
            ).all():
                neighbor_id = edge.to_node_id if edge.from_node_id == node_id else edge.from_node_id
                if neighbor_id not in visited:
                    visited[neighbor_id] = (node_id, edge)
                    if neighbor_id == to_node.id:
                        found = True
                        break
                    next_frontier.append(neighbor_id)
            if found:
                break
        frontier = next_frontier

    if not found:
        return {"found": False, "path": [], "hops": 0}

    # Reconstruct path
    path = []
    current_id = to_node.id
    while current_id != from_node.id:
        parent_id, edge = visited[current_id]
        node = db.query(Node).filter(Node.id == current_id).first()
        path.append({"node": node.to_dict() if node else None, "edge": edge.to_dict_with_nodes() if edge else None})
        current_id = parent_id

    # Add start node
    path.append({"node": from_node.to_dict(), "edge": None})
    path.reverse()

    return {"found": True, "path": path, "hops": len(path) - 1}


# ─── SYNC ENDPOINT ────────────────────────────────────────────────────────────

@app.post("/api/sync", response_model=SyncOut)
def trigger_sync(req: SyncRequest, db: Session = Depends(get_db)):
    """POST /api/sync — Trigger markdown → DB sync."""
    knowledge_path = os.environ.get(
        "KNOWLEDGE_PATH",
        os.path.expanduser("~/mywork/knowledge-graph"),
    )

    if not os.path.isdir(knowledge_path):
        raise HTTPException(
            status_code=400,
            detail=f"KNOWLEDGE_PATH '{knowledge_path}' not found. Set KNOWLEDGE_PATH env var.",
        )

    result = run_sync(knowledge_path, db, force=req.force)
    
    return {
        "status": result.status,
        "summary": result.to_dict(),
    }


# ─── STATS ENDPOINT ───────────────────────────────────────────────────────────

@app.get("/api/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    """GET /api/stats — Dashboard overview counts."""
    total_nodes = db.query(func.count(Node.id)).scalar() or 0
    total_edges = db.query(func.count(Edge.id)).scalar() or 0

    # by_kind
    kind_rows = (
        db.query(Node.kind, func.count(Node.id).label("cnt"))
        .group_by(Node.kind)
        .order_by(func.count(Node.id).desc())
        .all()
    )
    by_kind = {row.kind: row.cnt for row in kind_rows}

    # top_predicates
    pred_rows = (
        db.query(Edge.predicate, func.count(Edge.id).label("cnt"))
        .group_by(Edge.predicate)
        .order_by(func.count(Edge.id).desc())
        .limit(10)
        .all()
    )
    top_predicates = [{"predicate": row.predicate, "count": row.cnt} for row in pred_rows]

    # by_tag (parse JSON tags, count occurrences)
    tag_rows = db.query(Node.tags).filter(Node.tags.isnot(None)).all()
    tag_counts = {}
    for (tags_json,) in tag_rows:
        if tags_json:
            try:
                tags = json.loads(tags_json)
                if isinstance(tags, list):
                    for t in tags:
                        tag_counts[t] = tag_counts.get(t, 0) + 1
            except (json.JSONDecodeError, TypeError):
                pass
    by_tag = dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:20])

    # Last sync
    last_sync = db.query(SyncRun).order_by(SyncRun.started_at.desc()).first()

    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "by_kind": by_kind,
        "top_predicates": top_predicates,
        "by_tag": by_tag,
        "last_sync": last_sync.to_dict() if last_sync else None,
    }


# ─── LINT ENDPOINT ────────────────────────────────────────────────────────────

@app.get("/api/lint/prod")
def prod_lint(db: Session = Depends(get_db)):
    """GET /api/lint/prod — Production readiness lint report."""
    return run_prod_lint(db)


# ─── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
