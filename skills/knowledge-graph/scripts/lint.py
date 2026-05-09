#!/usr/bin/env python3
"""
Health check and maintenance for the knowledge graph.

Usage:
    python3 scripts/lint.py [options]

Options:
    --fix              Auto-fix minor issues (add missing index entries, etc.)
    --stale-days N     Warn if node updated > N days ago (default: 90)
    --knowledge-path PATH
    --json             Output as JSON

Checks:
1. Orphan nodes (zero inbound edges from other graph nodes)
2. Broken edges (link targets that don't exist as files)
3. Index completeness (every node file in index.md)
4. Index orphans (index entries whose files don't exist)
5. Contradictions (nodes linked via |rel:contradicts|
6. Stale nodes (last updated > N days)
7. Missing frontmatter
"""

import os
import sys
import json
import argparse
from datetime import date, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from graph import build_graph, find_nodes


def get_knowledge_path():
    env_path = os.environ.get("KNOWLEDGE_PATH")
    if env_path:
        return os.path.expanduser(env_path)
    return os.path.expanduser("~/mywork/knowledge-graph")


def parse_index(root: str) -> set[str]:
    """Parse index.md and return set of slugs mentioned."""
    index_path = os.path.join(root, "index.md")
    if not os.path.exists(index_path):
        return set()

    import re
    slugs = set()
    with open(index_path) as f:
        for line in f:
            m = re.findall(r'\[\[([^\]]+)\]\]', line)
            for slug in m:
                slugs.add(slug)
    return slugs


def find_all_node_files(root: str) -> list[Path]:
    """Find all markdown files that are node files (not schema/index/log/scripts/queries)."""
    skip_dirs = {"queries", "scripts", "templates"}
    skip_files = {"SCHEMA.md", "index.md", "log.md"}

    files = []
    for f in Path(root).rglob("*.md"):
        rel = str(f.relative_to(root))
        parts = rel.split(os.sep)
        if parts[0] in skip_dirs:
            continue
        if f.name in skip_files:
            continue
        files.append(f)
    return files


def node_slug_from_path(root: str, filepath: Path) -> str:
    """Derive the node slug from its file path relative to root."""
    rel = filepath.relative_to(root)
    stem = rel.with_suffix("")
    return str(stem)


def main():
    parser = argparse.ArgumentParser(description="Lint the knowledge graph")
    parser.add_argument("--fix", action="store_true", help="Auto-fix minor issues")
    parser.add_argument("--stale-days", type=int, default=90,
                        help="Warn if node updated > N days ago")
    parser.add_argument("--knowledge-path", default=None)
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    root = args.knowledge_path or get_knowledge_path()

    if not os.path.exists(root):
        print(f"Knowledge graph not found: {root}")
        return 1

    g = build_graph(root)
    issues = []

    # ── 1. Orphan nodes (zero inbound edges) ──────────────────────────
    inbound_count = {}
    for e in g.edges:
        inbound_count[e.target] = inbound_count.get(e.target, 0) + 1

    orphans = [n for n in g.nodes.values()
               if inbound_count.get(n.slug, 0) == 0]
    if orphans:
        issues.append({
            "type": "orphan_nodes",
            "severity": "warning",
            "count": len(orphans),
            "items": [n.slug for n in orphans],
            "message": f"{len(orphans)} orphan nodes (0 inbound edges from other nodes)"
        })

    # ── 2. Broken edges ───────────────────────────────────────────────
    broken = []
    for e in g.edges:
        if e.target not in g.nodes:
            broken.append((e.source, e.predicate, e.target))
    if broken:
        issues.append({
            "type": "broken_edges",
            "severity": "error",
            "count": len(broken),
            "items": [f"{s} |{p}| {t}" for s, p, t in broken],
            "message": f"{len(broken)} broken edge(s) (target node doesn't exist)"
        })

    # ── 3. Index completeness ─────────────────────────────────────────
    index_slugs = parse_index(root)
    node_slugs = set(g.nodes.keys())

    missing_from_index = node_slugs - index_slugs
    if missing_from_index:
        issues.append({
            "type": "missing_from_index",
            "severity": "warning",
            "count": len(missing_from_index),
            "items": sorted(missing_from_index),
            "message": f"{len(missing_from_index)} node(s) missing from index.md"
        })

    # ── 4. Index orphans ──────────────────────────────────────────────
    index_orphans = index_slugs - node_slugs
    if index_orphans:
        issues.append({
            "type": "index_orphans",
            "severity": "error",
            "count": len(index_orphans),
            "items": sorted(index_orphans),
            "message": f"{len(index_orphans)} index entries pointing to non-existent files"
        })

    # ── 5. Contradictions ─────────────────────────────────────────────
    contradictions = []
    for e in g.edges:
        if e.predicate == "contradicts":
            contradictions.append((e.source, e.target))
    if contradictions:
        issues.append({
            "type": "contradictions",
            "severity": "info",
            "count": len(contradictions),
            "items": [f"{a} ↔ {b}" for a, b in contradictions],
            "message": f"{len(contradictions)} contradiction(s) in graph"
        })

    # ── 6. Stale nodes ────────────────────────────────────────────────
    if args.stale_days > 0:
        today = date.today()
        stale = []
        for n in g.nodes.values():
            if n.updated:
                try:
                    updated_str = n.updated if isinstance(n.updated, str) else n.updated.isoformat()
                    updated_date = datetime.strptime(updated_str, "%Y-%m-%d").date()
                    delta = (today - updated_date).days
                    if delta > args.stale_days:
                        stale.append((n.slug, n.title, delta))
                except ValueError:
                    stale.append((n.slug, n.title, 0))
        if stale:
            issues.append({
                "type": "stale_nodes",
                "severity": "info",
                "count": len(stale),
                "items": [f"{s} ({t}, {d}d since update)" for s, t, d in stale],
                "message": f"{len(stale)} node(s) untouched in >{args.stale_days} days"
            })

    # ── 7. Missing or incomplete frontmatter ──────────────────────────
    from graph import parse_frontmatter

    bad_fm = []
    for node in g.nodes.values():
        meta, _ = parse_frontmatter(Path(node.path).read_text() if os.path.exists(node.path) else "")
        missing = []
        for field in ["title", "kind", "created", "updated"]:
            if field not in meta or not meta[field]:
                missing.append(field)
        if missing:
            bad_fm.append((node.slug, missing))
    if bad_fm:
        issues.append({
            "type": "incomplete_frontmatter",
            "severity": "warning",
            "count": len(bad_fm),
            "items": [f"{s}: missing {', '.join(m)}" for s, m in bad_fm],
            "message": f"{len(bad_fm)} node(s) with incomplete frontmatter"
        })

    # ── Report ────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps(issues, indent=2))
        return 0

    severity_order = {"error": 0, "warning": 1, "info": 2}

    print("=" * 60)
    print(f"Knowledge Graph Health Check: {root}")
    print(f"  Nodes: {len(g.nodes)}  Edges: {len(g.edges)}")
    print("=" * 60)

    if not issues:
        print("\nNo issues found. Graph is healthy.")
        return 0

    # Group by severity
    by_severity = {}
    for issue in issues:
        sev = issue["severity"]
        by_severity.setdefault(sev, []).append(issue)

    for sev in ["error", "warning", "info"]:
        for issue in by_severity.get(sev, []):
            sev_label = sev.upper()
            print(f"\n[{sev_label}] {issue['message']}")
            for item in issue.get("items", [])[:10]:  # Show first 10
                print(f"  - {item}")
            if len(issue.get("items", [])) > 10:
                print(f"  ... and {len(issue['items']) - 10} more")

    print("\n" + "=" * 60)
    total_by_severity = {s: len(v) for s, v in by_severity.items()}
    print(f"Summary: {total_by_severity.get('error', 0)} errors, "
          f"{total_by_severity.get('warning', 0)} warnings, "
          f"{total_by_severity.get('info', 0)} info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
