#!/usr/bin/env python3
"""
Sync markdown knowledge graph → NebulaGraph.

Reads all .md node files from ~/mywork/knowledge-graph/ and inserts vertices
and edges into a running NebulaGraph instance.

Usage:
    python3 sync_markdown_to_nebula.py [--graphd 127.0.0.1:9669] [--dry-run]
"""

import os, sys, re, time
from pathlib import Path
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

# Paths
KG_PATH = os.path.expanduser(os.environ.get("KNOWLEDGE_PATH", "~/mywork/knowledge-graph"))
NEBULA_SCRIPTS = Path.home() / ".hermes" / "skills" / "research" / "knowledge-graph" / "scripts"
sys.path.insert(0, str(NEBULA_SCRIPTS))
from graph import build_graph, INVERSE_MAP

GRAPH_HOST = "127.0.0.1"
GRAPH_PORT = 9669
USER = "root"
PASSWORD = "nebula"
SPACE = "knowledge_graph"

# Kind → NebulaGraph tag mapping
KIND_TO_TAG = {
    "person": "person", "people": "person",
    "organization": "organization", "organizations": "organization",
    "concept": "concept", "concepts": "concept",
    "tool": "tool", "tools": "tool",
    "project": "project", "projects": "project",
    "reference": "reference", "references": "reference",
    "spec": "spec", "specs": "spec",
    "requirement": "requirement", "requirements": "requirement",
    "scenario": "scenario", "scenarios": "scenario",
    "change": "delta", "changes": "delta",
    "design": "design",
    "task": "task", "tasks": "task",
}

# Predicates that are valid edge types (all 34 + their inverses)
ALL_EDGE_TYPES = set(INVERSE_MAP.keys()) | set(INVERSE_MAP.values())


def escape(s):
    """Escape a string for NebulaGraph nGQL."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def sync(g, client, dry_run=False):
    stats = {"vertices": 0, "edges": 0, "skipped_edges": 0}

    # ── 1. Insert vertices ──────────────────────────────────
    print(f"\nInserting {len(g.nodes)} vertices...")
    for slug, node in g.nodes.items():
        tag = KIND_TO_TAG.get(node.kind)
        if tag is None:
            print(f"  SKIP {slug}: unknown kind '{node.kind}'")
            continue

        # Truncate VID to 256 chars (NebulaGraph FIXED_STRING limit)
        vid = slug[:256]
        title = escape(node.title[:512]) if node.title else ""
        desc = ""
        tags_str = ",".join(node.tags[:20]) if node.tags else ""

        ngql = (
            f'INSERT VERTEX IF NOT EXISTS {tag}(name, title, description) '
            f'VALUES "{vid}":("{escape(node.title[:128])}", "{title}", "{desc}");'
        )

        if dry_run:
            stats["vertices"] += 1
            continue

        result = client.execute(ngql)
        if result.is_succeeded():
            stats["vertices"] += 1
        else:
            print(f"  ERROR vertex {slug}: {result.error_msg()}")

    # ── 2. Insert edges ─────────────────────────────────────
    print(f"\nInserting {len(g.edges)} edges...")
    for edge in g.edges:
        pred = edge.predicate

        # Normalize predicate to a valid edge type
        if pred not in ALL_EDGE_TYPES:
            stats["skipped_edges"] += 1
            continue

        src = edge.source[:256]
        dst = edge.target[:256]

        ngql = (
            f'INSERT EDGE {pred}(description) '
            f'VALUES "{src}"->"{dst}":("{pred}");'
        )

        if dry_run:
            stats["edges"] += 1
            continue

        result = client.execute(ngql)
        if result.is_succeeded():
            stats["edges"] += 1
        else:
            # Edge might fail if vertices don't exist yet — retry pattern
            stats["skipped_edges"] += 1

    return stats


def verify(client):
    """Run verification queries."""
    queries = [
        ("Total vertices", "MATCH (v) RETURN count(v) AS count;"),
        ("Total edges", "MATCH ()-[e]->() RETURN count(e) AS count;"),
        ("Top tags", "MATCH (v) RETURN id(v) AS vid LIMIT 5;"),
        ("Vedanta path", 
         "MATCH p=(a)-[*1..4]->(b) "
         "WHERE id(a)=='people/sri-ramakrishna' AND id(b)=='people/koustubh' "
         "RETURN p LIMIT 1;"),
    ]

    print("\n=== Verification Queries ===")
    for label, query in queries:
        result = client.execute(query)
        if result.is_succeeded():
            print(f"  {label}: {result.row_size()} row(s)")
            if result.row_size() > 0:
                for i in range(min(result.row_size(), 3)):
                    print(f"    {result.row_values(i)}")
        else:
            print(f"  {label}: ERROR — {result.error_msg()}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--graphd", default=f"{GRAPH_HOST}:{GRAPH_PORT}")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--knowledge-path", default=KG_PATH)
    args = parser.parse_args()

    host, port = args.graphd.split(":")
    port = int(port)

    # Build graph from markdown
    root = os.path.expanduser(args.knowledge_path)
    if not os.path.isdir(root):
        print(f"Knowledge graph not found: {root}")
        return 1

    print(f"Building graph from {root}...")
    g = build_graph(root)
    print(f"  {len(g.nodes)} nodes, {len(g.edges)} edges")

    if args.dry_run:
        stats = sync(g, None, dry_run=True)
        print(f"\nDRY RUN: would insert {stats['vertices']} vertices, {stats['edges']} edges")
        return 0

    # Connect to NebulaGraph
    config = Config()
    config.max_connection_pool_size = 2
    pool = ConnectionPool()
    pool.init([(host, port)], config)
    client = pool.get_session(USER, PASSWORD)

    result = client.execute(f"USE {SPACE};")
    if not result.is_succeeded():
        print(f"Failed to use space '{SPACE}': {result.error_msg()}")
        print("Run nebula_init.py first.")
        return 1

    stats = sync(g, client)
    print(f"\nSync complete: {stats['vertices']} vertices, {stats['edges']} edges, "
          f"{stats['skipped_edges']} skipped")

    verify(client)

    client.release()
    pool.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
