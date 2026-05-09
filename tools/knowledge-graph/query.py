#!/usr/bin/env python3
"""
Query the knowledge graph.

Usage:
    python3 scripts/query.py <seed> [options]
    python3 scripts/query.py --path <from> <to>
    python3 scripts/query.py --list-kinds
    python3 scripts/query.py --stats

Options:
    --depth N         Max traversal depth (default: 2)
    --via PREDICATE   Filter edges by predicate
    --of-kind KIND    Only return nodes of this kind
    --path A B        Find shortest path between two nodes
    --save NAME       Save this query as a reusable pattern
    --format {json,text}  Output format (default: text if --save, else text)
    --knowledge-path PATH

Examples:
    python3 scripts/query.py koustubh --depth 3
    python3 scripts/query.py koustubh --via influences --of-kind concept
    python3 scripts/query.py --path vedanta options-screener
    python3 scripts/query.py --stats
    python3 scripts/query.py --list-kinds
"""

import os
import sys
import json
import argparse
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from graph import build_graph, find_nodes, format_subgraph


def get_knowledge_path():
    env_path = os.environ.get("KNOWLEDGE_PATH")
    if env_path:
        return os.path.expanduser(env_path)
    return os.path.expanduser("~/mywork/knowledge-graph")


def save_query(root: str, name: str, query_type: str, params: dict, result: dict):
    """Save a query pattern to queries/."""
    queries_dir = os.path.join(root, "queries")
    os.makedirs(queries_dir, exist_ok=True)

    filepath = os.path.join(queries_dir, f"{name}.md")
    today = date.today().isoformat()

    content = f"""---
name: {name}
kind: query
created: {today}
updated: {today}
query_type: {query_type}
params: {json.dumps(params)}
---

# Query: {name}

## Pattern

This query finds nodes connected to the seed via the specified traversal.

## Parameters
| Param | Description |
|-------|-------------|
| seed | Starting node slug |
| depth | Max traversal depth |

## Result Summary (at creation)

{len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges

```json
{json.dumps(result, indent=2)}
```
"""
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Query saved to: {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Query the knowledge graph")
    parser.add_argument("seed", nargs="?", default=None, help="Seed node slug or search term")
    parser.add_argument("--depth", type=int, default=2, help="Max traversal depth")
    parser.add_argument("--via", default=None, help="Filter edges by predicate")
    parser.add_argument("--of-kind", default=None, help="Only return nodes of this kind")
    parser.add_argument("--path", nargs=2, metavar=("FROM", "TO"), help="Find shortest path")
    parser.add_argument("--save", default=None, help="Save query pattern with this name")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                        help="Output format")
    parser.add_argument("--stats", action="store_true", help="Show graph stats")
    parser.add_argument("--list-kinds", action="store_true", help="List all node kinds in use")
    parser.add_argument("--knowledge-path", default=None, help="Knowledge graph root path")
    parser.add_argument("--edge", default=None, help="Alias for --via")

    args = parser.parse_args()

    root = args.knowledge_path or get_knowledge_path()

    if not os.path.exists(root):
        print(f"Knowledge graph not found at: {root}")
        print("Create it with: mkdir -p {root}")
        return 1

    g = build_graph(root)

    # Stats mode
    if args.stats:
        kinds = {}
        for n in g.nodes.values():
            kinds[n.kind] = kinds.get(n.kind, 0) + 1
        pred_counts = {}
        for e in g.edges:
            pred_counts[e.predicate] = pred_counts.get(e.predicate, 0) + 1

        print(f"Knowledge Graph: {root}")
        print(f"  Nodes: {len(g.nodes)}")
        print(f"  Edges: {len(g.edges)}")
        print(f"\nNode kinds:")
        for k, c in sorted(kinds.items(), key=lambda x: -x[1]):
            print(f"  {k:20s} {c}")
        print(f"\nPredicates used:")
        for p, c in sorted(pred_counts.items(), key=lambda x: -x[1]):
            if c > 0:
                print(f"  {p:20s} {c}")
        return 0

    # List kinds mode
    if args.list_kinds:
        kinds = set()
        for n in g.nodes.values():
            kinds.add(n.kind)
        print("Node kinds in use:")
        for k in sorted(kinds):
            count = sum(1 for n in g.nodes.values() if n.kind == k)
            print(f"  {k} ({count})")
        return 0

    # Path mode
    if args.path:
        from_slug, to_slug = args.path
        from_nodes = find_nodes(g, from_slug)
        to_nodes = find_nodes(g, to_slug)

        if not from_nodes:
            print(f"No node found matching: {from_slug}")
            return 1
        if not to_nodes:
            print(f"No node found matching: {to_slug}")
            return 1

        from_id = from_nodes[0].slug
        to_id = to_nodes[0].slug

        path = g.shortest_path(from_id, to_id)
        if path is None:
            print(f"No path found between '{from_id}' and '{to_id}'")
        else:
            print(f"Path ({len(path)} hops):")
            for hop in path:
                print(f"  {hop['from']} |{hop['predicate']}| → {hop['to']}")

        if args.save:
            result = {"path": path, "from": from_id, "to": to_id}
            save_query(root, args.save, "path",
                       {"from": from_slug, "to": to_slug}, result)
        return 0

    # Seed-based traversal
    if not args.seed:
        parser.print_help()
        return 1

    seed_nodes = find_nodes(g, args.seed)
    if not seed_nodes:
        print(f"No nodes found matching: '{args.seed}'")
        print(f"Try: python3 scripts/query.py --list-kinds")
        return 1

    seed_ids = [n.slug for n in seed_nodes]

    # Traverse
    predicates = [args.via] if args.via else None
    sub = g.traverse(seed_ids, predicates=predicates, max_depth=args.depth)

    # Filter by kind if requested
    if args.of_kind:
        kind_nodes = {s: n for s, n in sub.nodes.items() if n.kind == args.of_kind}
        kind_edges = [e for e in sub.edges
                      if e.source in kind_nodes or e.target in kind_nodes]
        sub.nodes = kind_nodes
        sub.edges = kind_edges

    result = sub.to_dict()

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_subgraph(sub))

    # Save if requested
    if args.save:
        save_query(root, args.save, "traversal",
                   {"seed": args.seed, "depth": args.depth,
                    "via": args.via, "of_kind": args.of_kind},
                   result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
