"""
knowledge-graph core library.
Parse markdown node files, build adjacency graph, traverse with typed edges.
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict, deque
from typing import Optional

# ── Inverse predicate map ──────────────────────────────────────────────
# Every predicate has a natural inverse. When we add an edge A ->rel-> B,
# we also add B ->inv_rel-> A so traversal works in both directions.
INVERSE_MAP = {
    "is_a":          "has_instance",
    "same_as":       "same_as",           # symmetric
    "portion_of":    "contains",
    "follows":       "followed_by",
    "values":        "valued_by",
    "rejects":       "rejected_by",
    "prefers":       "preferred_by",
    "influences":    "influenced_by",
    "enables":       "enabled_by",
    "blocks":        "blocked_by",
    "depends_on":    "depended_upon_by",
    "uses":          "used_by",
    "produces":      "produced_by",
    "precedes":      "succeeds",
    "supersedes":    "superseded_by",
    "attests":       "attested_by",
    "contradicts":   "contradicts",       # symmetric
    "goals_for":     "goal_of",
    "constrains":    "constrained_by",
    "teaches":       "taught_by",
    "builds":        "built_by",

    # ── Software specification predicates (OpenSpec-adapted) ──────────
    "exposes":       "exposed_by",
    "accepts":       "accepted_by",
    "returns":       "returned_by",
    "triggers":      "triggered_by",
    "fails_with":    "failed_by",
    "spec_of":       "specified_by",
    "scenario_for":  "has_scenario",
    "change_for":    "changed_by",
    "adds":          "added_by",
    "modifies":      "modified_by",
    "removes":       "removed_by",
    "archives_to":   "archived_from",
    "tests":         "tested_by",
    "guarantees":    "guaranteed_by",
    "implements":    "implemented_by",
    "conforms_to":   "conformed_by",
    "touches":       "touched_by",
    "reuses":        "reused_by",
    "deploys_to":    "hosts",
    "shares_schema_with": "shares_schema_with",  # symmetric
    "authenticates_via": "authenticates",
}

# ── Edge regex ─────────────────────────────────────────────────────────
EDGE_RE = re.compile(r'\|rel:(\w+)\|\s*\[\[([^\]]+)\]\]')

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown text. Returns (meta, body)."""
    m = FRONTMATTER_RE.match(text)
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
            # Ensure dates are strings, not date objects
            for field in ["created", "updated"]:
                if field in meta and not isinstance(meta[field], str):
                    meta[field] = meta[field].isoformat() if hasattr(meta[field], 'isoformat') else str(meta[field])
        except yaml.YAMLError:
            meta = {}
        body = text[m.end():].strip()
    else:
        meta = {}
        body = text.strip()
    return meta, body


def parse_edges(text: str) -> list[tuple[str, str]]:
    """Extract (predicate, target_path) pairs from markdown text."""
    return [(m.group(1), m.group(2)) for m in EDGE_RE.finditer(text)]


# ── Graph data structures ──────────────────────────────────────────────

class Node:
    __slots__ = ('path', 'slug', 'title', 'kind', 'tags', 'created', 'updated')
    def __init__(self, path: str, slug: str, title: str, kind: str = "unknown",
                 tags: list[str] = None, created=None, updated=None):
        created = created.isoformat() if hasattr(created, 'isoformat') else (created or "")
        updated = updated.isoformat() if hasattr(updated, 'isoformat') else (updated or "")
        self.path = path
        self.slug = slug
        self.title = title
        self.kind = kind
        self.tags = tags or []
        self.created = created
        self.updated = updated

    def to_dict(self):
        return {
            "id": self.slug,
            "title": self.title,
            "kind": self.kind,
            "tags": self.tags,
            "path": self.path,
        }


class Edge:
    __slots__ = ('source', 'target', 'predicate')
    def __init__(self, source: str, target: str, predicate: str):
        self.source = source
        self.target = target
        self.predicate = predicate

    def to_dict(self):
        return {"source": self.source, "target": self.target, "predicate": self.predicate}


class Graph:
    """Adjacency list with typed edges. node_id -> list of (edge_predicate, target_id)."""

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self._adj_by_pred: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    def add_node(self, node: Node):
        self.nodes[node.slug] = node

    def add_edge(self, source: str, target: str, predicate: str):
        self.edges.append(Edge(source, target, predicate))
        self.adj[source].append((predicate, target))
        self._adj_by_pred[predicate][source].append(target)

    def get_node(self, slug: str) -> Optional[Node]:
        return self.nodes.get(slug)

    def neighbors(self, slug: str, predicate: str = None) -> list[tuple[str, str]]:
        """Get neighbors of a node. Optionally filter by predicate."""
        if predicate:
            return [(predicate, t) for t in self._adj_by_pred[predicate].get(slug, [])]
        return self.adj.get(slug, [])

    def traverse(self, seeds: list[str], predicates: list[str] = None,
                 max_depth: int = 2) -> 'Graph':
        """BFS traversal from seeds. Returns a subgraph."""
        sub = Graph()
        visited = set(seeds)
        queue = deque((s, 0) for s in seeds)

        # Add seed nodes
        for s in seeds:
            if s in self.nodes:
                sub.add_node(self.nodes[s])

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for pred, target in self.adj.get(current, []):
                if predicates and pred not in predicates:
                    continue
                if target not in visited:
                    visited.add(target)
                    if target in self.nodes:
                        sub.add_node(self.nodes[target])
                    sub.add_edge(current, target, pred)
                    queue.append((target, depth + 1))
                else:
                    # Still add the edge if both nodes in subgraph
                    if current in sub.nodes and target in sub.nodes:
                        sub.add_edge(current, target, pred)
        return sub

    def shortest_path(self, source: str, target: str,
                      max_depth: int = 6) -> Optional[list[dict]]:
        """BFS shortest path. Returns list of hops or None."""
        if source not in self.nodes or target not in self.nodes:
            return None
        visited = {source}
        queue = deque([(source, [])])
        while queue:
            current, path = queue.popleft()
            for pred, neighbor in self.adj.get(current, []):
                hop = {"from": current, "to": neighbor, "predicate": pred}
                new_path = path + [hop]
                if neighbor == target:
                    return new_path
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, new_path))
                    if len(new_path) >= max_depth:
                        continue
        return None

    def filter_by_kind(self, kind: str) -> list[Node]:
        return [n for n in self.nodes.values() if n.kind == kind]

    def to_dict(self):
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }


# ── Build graph from directory ─────────────────────────────────────────

def build_graph(root: str) -> Graph:
    """Scan knowledge directory, parse all .md files into a Graph."""
    root = os.path.expanduser(root)
    g = Graph()

    # Skip SCHEMA.md, index.md, log.md, and queries/
    skip_dirs = {"queries", "scripts", "templates"}
    skip_files = {"SCHEMA.md", "index.md", "log.md"}

    for md_file in Path(root).rglob("*.md"):
        rel = md_file.relative_to(root)
        parts = rel.parts

        # Skip non-node files
        if parts[0] in skip_dirs:
            continue
        if rel.name in skip_files:
            continue

        text = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)

        # Derive slug from relative path (without .md extension)
        slug = str(rel.parent / rel.stem) if rel.parent.name != "." else rel.stem

        node = Node(
            path=str(md_file),
            slug=slug,
            title=meta.get("title", rel.stem.replace("-", " ").title()),
            kind=meta.get("kind", parts[0] if len(parts) > 1 else "unknown"),
            tags=meta.get("tags", []),
            created=meta.get("created", ""),
            updated=meta.get("updated", ""),
        )
        g.add_node(node)

        # Extract edges from body
        for pred, target_slug in parse_edges(body):
            g.add_edge(slug, target_slug, pred)

    return g


def find_nodes(g: Graph, query: str) -> list[Node]:
    """Fuzzy find nodes by slug, title, or tag match.
    Results sorted by match quality: exact slug > slug substring > title match > tag match."""
    q = query.lower()
    scored = []
    for node in g.nodes.values():
        slug_lower = node.slug.lower()
        title_lower = node.title.lower()

        # Exact slug match (highest priority)
        if q == slug_lower or slug_lower.endswith(f"/{q}") or slug_lower == q:
            scored.append((0, node))
        elif q in slug_lower:
            scored.append((1, node))
        elif q in title_lower:
            scored.append((2, node))
        else:
            for tag in node.tags:
                if isinstance(tag, str) and q in tag.lower():
                    scored.append((3, node))
                    break

    return [node for _, node in sorted(scored, key=lambda x: x[0])]


def format_subgraph(sub: Graph) -> str:
    """Format a subgraph as readable text for display."""
    lines = []
    lines.append(f"Subgraph: {len(sub.nodes)} nodes, {len(sub.edges)} edges")
    lines.append("")
    for node in sub.nodes.values():
        lines.append(f"  [{node.kind:16s}] {node.title}")
        for pred, target in sub.neighbors(node.slug):
            t = sub.get_node(target)
            tname = t.title if t else target
            lines.append(f"    |{pred:16s}| ─→ {tname}")
    return "\n".join(lines)
