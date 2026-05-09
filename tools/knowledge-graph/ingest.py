#!/usr/bin/env python3
"""
Ingest a fact into the knowledge graph as a subject-predicate-object triple.

Usage:
    python3 scripts/ingest.py <subject> <predicate> <object> [options]

Options:
    --subject-kind KIND    Default: inferred from context
    --object-kind KIND     Default: inferred from first path segment
    --tags "tag1,tag2"     Tags for the object node
    --title "Title"        Override auto-generated title
    --force                Overwrite existing node content
    --knowledge-path PATH  Override default knowledge path

Examples:
    python3 scripts/ingest.py koustubh follows ramakrishna-mission --object-kind organization
    python3 scripts/ingest.py koustubh values systems-thinking --object-kind concept
    python3 scripts/ingest.py koustubh builds options-screener --object-kind project --tags "trading,python"
"""

import os
import sys
import argparse
from datetime import date
from pathlib import Path

# Add parent dir so we can import graph.py
SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from graph import build_graph, find_nodes, INVERSE_MAP


def get_knowledge_path():
    env_path = os.environ.get("KNOWLEDGE_PATH")
    if env_path:
        return os.path.expanduser(env_path)
    return os.path.expanduser("~/mywork/knowledge-graph")


KIND_PLURAL_MAP = {
    "people": "people", "person": "people",
    "concept": "concepts", "concepts": "concepts",
    "project": "projects", "projects": "projects",
    "tool": "tools", "tools": "tools",
    "organization": "organizations", "organizations": "organizations",
    "spec": "specs", "specs": "specs",
    "requirement": "requirements", "requirements": "requirements",
    "scenario": "scenarios", "scenarios": "scenarios",
    "change": "changes", "changes": "changes",
    "design": "designs", "designs": "designs",
    "task": "tasks", "tasks": "tasks",
    "reference": "references", "references": "references",
    "query": "queries", "queries": "queries",
}


def ensure_dir(root: str, kind: str) -> str:
    """Ensure the subdirectory for a node kind exists."""
    d = os.path.join(root, kind)
    os.makedirs(d, exist_ok=True)
    return d


def slug_from_name(name: str) -> str:
    """Convert a name to a slug."""
    return name.strip().lower().replace(" ", "-").replace("_", "-")


def guess_kind_from_slug(slug: str) -> str:
    """If slug looks like 'people/foo', extract kind from first segment."""
    parts = slug.split("/")
    if len(parts) > 1:
        return parts[0]
    return "concept"  # default


def node_file_path(root: str, kind: str, slug: str) -> str:
    """Get the file path for a node."""
    if "/" in slug:
        # slug already has kind prefix
        return os.path.join(root, f"{slug}.md")
    return os.path.join(root, kind, f"{slug}.md")


def node_exists(root: str, slug: str) -> bool:
    """Check if a node file exists."""
    return any(
        Path(root).rglob(f"*/{slug}.md")
    )


def find_node_file(root: str, slug: str):
    """Find a node file by slug anywhere in the graph."""
    for f in Path(root).rglob(f"**/{slug}.md"):
        return str(f)
    return None


def read_or_create_node(root: str, slug: str, kind: str,
                         title: str = None, tags: list = None) -> str:
    """Read existing node file or create a new one. Returns file path."""
    if title is None:
        title = slug.replace("-", " ").title().replace("/", " — ")
    if tags is None:
        tags = []

    existing = find_node_file(root, slug)
    if existing:
        return existing

    # Create new node
    full_slug = slug
    if "/" not in full_slug:
        full_slug = f"{kind}/{slug}"
        dir_path = ensure_dir(root, kind)
    else:
        # Ensure the directory exists
        dir_path = os.path.join(root, os.path.dirname(full_slug))
        os.makedirs(dir_path, exist_ok=True)

    filepath = os.path.join(root, f"{full_slug}.md")
    today = date.today().isoformat()

    content = f"""---
title: {title}
kind: {kind}
created: {today}
updated: {today}
tags: [{', '.join(tags)}]
---

# {title}

"""
    with open(filepath, "w") as f:
        f.write(content)

    return filepath


def add_edge_to_file(filepath: str, predicate: str, target_slug: str):
    """Add an edge line to a node file if it doesn't already exist."""
    edge_line = f"|rel:{predicate}| [[{target_slug}]]\n"
    with open(filepath, "r") as f:
        content = f.read()

    if edge_line.strip() in content:
        return  # already exists

    # Insert before any trailing blank lines at the end
    if content.endswith("\n\n"):
        content = content.rstrip() + "\n" + edge_line
    elif content.endswith("\n"):
        content = content + edge_line
    else:
        content = content + "\n" + edge_line

    with open(filepath, "w") as f:
        f.write(content)

    # Update the 'updated' field in frontmatter
    update_frontmatter_date(filepath)


def update_frontmatter_date(filepath: str):
    """Bump the updated: date in YAML frontmatter."""
    with open(filepath, "r") as f:
        content = f.read()

    if not content.startswith("---"):
        return

    import re
    today = date.today().isoformat()
    # Replace existing updated date
    new_content = re.sub(
        r'^updated:.*$',
        f'updated: {today}',
        content,
        count=1,
        flags=re.MULTILINE
    )
    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)


def update_index(root: str, node_title: str, node_slug: str, kind: str):
    """Add a node entry to index.md under the correct section."""
    index_path = os.path.join(root, "index.md")
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write("# Knowledge Graph Index\n\n")

    with open(index_path, "r") as f:
        content = f.read()

    # Find the right section header
    section_header = f"## {kind.title()}s\n"
    entry = f"- [[{node_slug}]] — {node_title}\n"

    if section_header in content:
        # Check if already in index
        if entry.strip() in content:
            return
        # Insert after the section header (find the header and add after it)
        idx = content.index(section_header) + len(section_header)
        # Find the next blank line or section
        rest = content[idx:]
        insert_at = idx
        for i, ch in enumerate(rest):
            if ch == '\n' and rest[i-1:i+1] != '\n\n':
                pass
            if rest[i:i+2] == '\n\n' or rest[i:i+3] == '\n##':
                insert_at = idx + i
                break
        else:
            insert_at = len(content)

        content = content[:insert_at] + "\n" + entry.rstrip() + content[insert_at:]
    else:
        content += f"\n{section_header}\n{entry}"

    with open(index_path, "w") as f:
        f.write(content)


def append_log(root: str, action: str, details: str):
    """Append to log.md."""
    log_path = os.path.join(root, "log.md")
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("# Knowledge Graph Log\n\n")

    today = date.today().isoformat()
    entry = f"## [{today}] {action}\n- {details}\n\n"

    with open(log_path, "a") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="Ingest a fact into the knowledge graph")
    parser.add_argument("subject", help="Subject slug (e.g., 'koustubh')")
    parser.add_argument("predicate", help="Predicate from the universal set")
    parser.add_argument("object", help="Object slug (e.g., 'vedanta')")
    parser.add_argument("--subject-kind", default=None, help="Kind of the subject node")
    parser.add_argument("--object-kind", default=None, help="Kind of the object node")
    parser.add_argument("--title", default=None, help="Title for the object node (auto-generated if absent)")
    parser.add_argument("--tags", default="", help="Comma-separated tags for the object node")
    parser.add_argument("--over", default=None, help="For 'prefers' predicate: preferred over what")
    parser.add_argument("--knowledge-path", default=None, help="Knowledge graph root path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing node content")

    args = parser.parse_args()

    root = args.knowledge_path or get_knowledge_path()
    os.makedirs(root, exist_ok=True)

    # Resolve slugs
    subj_slug = slug_from_name(args.subject)
    obj_slug = slug_from_name(args.object)
    pred = args.predicate.lower()

    # Infer kinds if not provided, then normalize to plural directories
    subj_kind = args.subject_kind or guess_kind_from_slug(subj_slug) or "concepts"
    subj_kind = KIND_PLURAL_MAP.get(subj_kind, subj_kind)
    obj_kind = args.object_kind or guess_kind_from_slug(obj_slug) or "concepts"
    obj_kind = KIND_PLURAL_MAP.get(obj_kind, obj_kind)

    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    # Handle predicates that take an extra target
    if pred == "prefers" and args.over:
        over_slug = slug_from_name(args.over)
        over_kind = args.object_kind or "concepts"
        over_kind = KIND_PLURAL_MAP.get(over_kind, over_kind)
        # Create/update the 'over' object too
        over_file = read_or_create_node(root, over_slug, over_kind)
        add_edge_to_file(over_file, INVERSE_MAP.get("prefers", "preferred_by"), subj_slug)

    # Create or read subject node
    subj_file = read_or_create_node(root, subj_slug, subj_kind, tags=tags)
    # Derive kind from actual directory (not frontmatter, which may be singular)
    subj_kind = os.path.relpath(subj_file, root).split(os.sep)[0]

    # Create or read object node
    obj_file = read_or_create_node(root, obj_slug, obj_kind,
                                    title=args.title, tags=tags)
    obj_kind = os.path.relpath(obj_file, root).split(os.sep)[0]

    # Compute full slugs with kind prefix (matching existing convention)
    subj_full_slug = f"{subj_kind}/{subj_slug}" if "/" not in subj_slug else subj_slug
    obj_full_slug = f"{obj_kind}/{obj_slug}" if "/" not in obj_slug else obj_slug

    # Add forward edge
    add_edge_to_file(subj_file, pred, obj_full_slug)

    # Add reverse edge if defined
    inv_pred = INVERSE_MAP.get(pred)
    if inv_pred:
        add_edge_to_file(obj_file, inv_pred, subj_full_slug)

    # Update index
    update_index(root, subj_full_slug.replace("-", " ").title(), subj_full_slug, subj_kind)
    update_index(root, obj_full_slug.replace("-", " ").title(), obj_full_slug, obj_kind)

    # Log
    detail = f"`{subj_full_slug}` |{pred}| `{obj_full_slug}`"
    if args.over:
        detail += f" (over `{slug_from_name(args.over)}`)"
    append_log(root, f"ingest: {subj_slug} {pred} {obj_slug}", detail)

    print(f"Ingested: {subj_slug} |{pred}| {obj_slug}")
    print(f"  Subject: {subj_file}")
    print(f"  Object:  {obj_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
