"""
Sync Engine: Markdown files → SQLAlchemy database.

sync-engine-spec:
  - incremental-sync [SHALL]: skip files with matching source_mtime
  - edge-reconciliation [SHALL]: delete+reinsert edges per node
  - error-tolerant-parsing [SHALL]: graceful handling of malformed files
  - sync-run-logging [SHOULD]: record each sync operation
"""

import os
import re
import time
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session
from models import Node, Edge, SyncRun, VALID_NODE_KINDS


# Directories to skip during walk
SKIP_DIRS = {"queries", "scripts", "templates", ".git", "__pycache__"}

# YAML frontmatter regex: --- ... ---
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

# Edge regex: |rel:PREDICATE| [[KIND/SLUG]]
EDGE_RE = re.compile(r"\|rel:(\w+)\|\s*\[\[([\w\-]+)/([\w\-]+)\]\]")

# Inverse predicate mapping (mirrors graph.py's INVERSE_MAP)
INVERSE_MAP = {
    "contains": "portion_of",
    "portion_of": "contains",
    "spec_of": "spec_of",
    "exposes": "exposed_by",
    "exposed_by": "exposes",
    "accepts": "accepted_by",
    "returns": "returned_by",
    "depends_on": "depended_by",
    "influences": "influenced_by",
    "reuses": "reused_by",
    "triggers": "triggered_by",
    "enables": "enabled_by",
    "blocks": "blocked_by",
    "constrains": "constrained_by",
    "adds": "added_by",
    "modifies": "modified_by",
    "removes": "removed_by",
    "archives_to": "archived_by",
    "scenario_for": "has_scenario",
    "tests": "tested_by",
    "guarantees": "guaranteed_by",
    "implements": "implemented_by",
    "conforms_to": "conformed_by",
    "teaches": "taught_by",
    "follows": "followed_by",
    "values": "valued_by",
    "rejects": "rejected_by",
    "precedes": "succeeded_by",
    "supersedes": "superseded_by",
    "superseded_by": "supersedes",
    "prefers": "preferred_by",
    "uses": "used_by",
    "builds": "built_by",
    "produces": "produced_by",
    "attests": "attested_by",
    "contradicts": "contradicts",
    "goals_for": "goaled_by",
    "is_a": "instance_of",
    "same_as": "same_as",
    "portion_of": "contains",
    "change_for": "has_change",
    "deploys_to": "deployed_by",
    "authenticates_via": "authenticator_for",
    "shares_schema_with": "shares_schema_with",
    "touches": "touched_by",
    "has_instance": "instance_of",
}


# ─── PARSING ──────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str):
    """Extract YAML frontmatter from markdown content.
    
    Returns (frontmatter_dict, body_text). Returns ({}, content) if no frontmatter.
    """
    match = FM_RE.match(content)
    if not match:
        return {}, content.strip()
    try:
        fm = yaml.safe_load(match.group(1))
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        return {}, content
    body = content[match.end():].strip()
    return fm, body


def parse_edges(body: str):
    """Parse |rel:PREDICATE| [[KIND/SLUG]] edges from body text.
    
    Returns deduplicated list of (predicate, kind, slug) tuples.
    """
    edges = []
    seen = set()
    for match in EDGE_RE.finditer(body):
        predicate = match.group(1)
        kind = match.group(2)
        slug = match.group(3)
        key = (predicate, kind, slug)
        if key not in seen:
            seen.add(key)
            edges.append(key)
    return edges


def infer_kind_from_dir(filepath: str, root: str) -> str:
    """Infer node kind from parent directory name, e.g. specs/ → spec."""
    rel = os.path.relpath(os.path.dirname(filepath), root)
    dir_name = rel.split(os.sep)[0] if rel != "." else "concepts"
    # Plural → singular mapping
    PLURAL_MAP = {
        "specs": "spec", "requirements": "requirement", "scenarios": "scenario",
        "changes": "change", "designs": "design", "concepts": "concept",
        "tasks": "task", "tools": "tool", "people": "person",
        "organizations": "organization", "references": "reference",
        "projects": "project",
    }
    return PLURAL_MAP.get(dir_name, "concept")


def slug_from_filename(filename: str) -> str:
    """Strip .md extension for slug."""
    return os.path.splitext(os.path.basename(filename))[0]


def title_from_slug(slug: str) -> str:
    """Auto-generate title from slug: 'hello-world' → 'Hello World'."""
    return slug.replace("-", " ").title()


# ─── DIRECTORY WALK ───────────────────────────────────────────────────────────

def collect_markdown_files(root: str):
    """Walk KNOWLEDGE_PATH and return all .md files, excluding SKIP_DIRS."""
    files = []
    root = os.path.expanduser(root)
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip directories in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".md"):
                files.append(os.path.join(dirpath, fn))
    return sorted(files)


# ─── NODE LOOKUP / UPSERT ─────────────────────────────────────────────────────

def find_node_by_slug(db: Session, slug: str):
    return db.query(Node).filter(Node.slug == slug).first()


def upsert_node(db: Session, slug: str, kind: str, title: str, body: str,
                fm: dict, source_file: str, source_mtime: float) -> Node:
    """Create or update a node from parsed markdown data."""
    node = find_node_by_slug(db, slug)
    now = datetime.now(timezone.utc)

    if node:
        # Update
        node.kind = kind
        node.title = title
        node.body = body
        node.source_file = source_file
        node.source_mtime = source_mtime
        node.updated_at = now

        # Update frontmatter fields if present
        if fm.get("tags"):
            node.tags = json.dumps(fm["tags"]) if isinstance(fm["tags"], list) else json.dumps([fm["tags"]])
        if fm.get("strength"):
            node.strength = fm["strength"]
        if fm.get("status"):
            node.status = fm["status"]
        if fm.get("meta_json"):
            node.meta_json = json.dumps(fm["meta_json"]) if isinstance(fm["meta_json"], dict) else "{}"
    else:
        # Create
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        node = Node(
            slug=slug,
            kind=kind,
            title=title,
            body=body,
            tags=json.dumps(tags),
            strength=fm.get("strength"),
            status=fm.get("status", "proposed"),
            source_file=source_file,
            source_mtime=source_mtime,
        )
        db.add(node)

    db.flush()
    return node


# ─── EDGE SYNC ────────────────────────────────────────────────────────────────

def resolve_edge_target(db: Session, kind: str, slug: str, warnings: list):
    """Find a target node ID for an edge. Create placeholder if missing."""
    target = find_node_by_slug(db, slug)
    if target:
        return target.id

    # Create placeholder reference node
    placeholder = Node(
        slug=slug,
        kind="reference",
        title=title_from_slug(slug),
        body=f"*Auto-created placeholder for unresolved edge target `{kind}/{slug}`*",
    )
    db.add(placeholder)
    db.flush()
    warnings.append(f"Created placeholder node '{slug}' (kind=reference) for unresolved edge")
    return placeholder.id


def sync_edges_for_node(db: Session, node_id: int, parsed_edges: list, warnings: list) -> tuple:
    """Replace all outgoing edges for a node with parsed_edges.
    
    Returns (edges_created, edges_removed).
    """
    # Delete existing outgoing edges using bulk SQL (immediate within tx)
    from sqlalchemy import text as sa_text
    removed = db.execute(
        sa_text("DELETE FROM edges WHERE from_node_id = :nid"),
        {"nid": node_id}
    ).rowcount
    db.flush()

    # Insert new edges
    created = 0
    for predicate, target_kind, target_slug in parsed_edges:
        target_id = resolve_edge_target(db, target_kind, target_slug, warnings)
        if target_id == node_id:
            warnings.append(f"Skipped circular edge {predicate} on node {node_id}")
            continue
        try:
            edge = Edge(
                from_node_id=node_id,
                to_node_id=target_id,
                predicate=predicate,
            )
            db.add(edge)
            created += 1
        except Exception:
            # Duplicate edge from another node's sync — skip silently
            pass

    db.flush()
    return created, removed


# ─── DELETION DETECTION ───────────────────────────────────────────────────────

def delete_removed_files(db: Session, synced_files: set) -> int:
    """Delete nodes whose source_file no longer exists on disk.
    
    Returns count of deleted nodes.
    """
    orphans = (
        db.query(Node)
        .filter(Node.source_file.isnot(None))
        .filter(~Node.source_file.in_(synced_files))
        .all()
    )
    count = 0
    for node in orphans:
        db.delete(node)
        count += 1
    db.flush()
    return count


# ─── MAIN SYNC FUNCTION ───────────────────────────────────────────────────────

def run_sync(knowledge_path: str, db: Session, force: bool = False) -> SyncRun:
    """
    Execute a full sync from markdown files to the database.
    
    Args:
        knowledge_path: Path to the knowledge-graph directory
        db: SQLAlchemy session
        force: If True, re-parse all files regardless of mtime
    
    Returns:
        SyncRun record with summary stats
    """
    knowledge_path = os.path.expanduser(knowledge_path)
    sync_run = SyncRun(status="running")
    db.add(sync_run)
    db.flush()

    try:
        files = collect_markdown_files(knowledge_path)
        synced_files = set()
        warnings = []
        errors = []

        nodes_created = 0
        nodes_updated = 0
        edges_created_total = 0
        edges_removed_total = 0

        for filepath in files:
            rel_path = os.path.relpath(filepath, knowledge_path)
            synced_files.add(rel_path)
            current_mtime = os.path.getmtime(filepath)

            # Incremental sync: skip if mtime matches (and not forced)
            if not force:
                existing = (
                    db.query(Node)
                    .filter(Node.source_file == rel_path)
                    .first()
                )
                if existing and existing.source_mtime == current_mtime:
                    continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                errors.append(f"Can't read {rel_path}: {e}")
                continue

            # Parse
            fm, body = parse_frontmatter(content)
            if fm is None:
                warnings.append(f"Malformed YAML frontmatter in {rel_path}")
                fm = {}

            # Derive fields
            slug = slug_from_filename(filepath)
            kind = fm.get("kind") or infer_kind_from_dir(filepath, knowledge_path)

            # Normalize plural kinds from frontmatter to singular
            KIND_NORMALIZE = {
                "specs": "spec", "requirements": "requirement", "scenarios": "scenario",
                "changes": "change", "designs": "design", "concepts": "concept",
                "tasks": "task", "tools": "tool", "people": "person",
                "organizations": "organization", "references": "reference",
                "projects": "project",
            }
            kind = KIND_NORMALIZE.get(kind, kind)

            title = fm.get("title") or title_from_slug(slug)

            # Upsert node
            try:
                node = upsert_node(db, slug, kind, title, body, fm, rel_path, current_mtime)
            except Exception as e:
                errors.append(f"Failed to upsert node from {rel_path}: {e}")
                continue

            if node.source_mtime != current_mtime:  # was updated
                nodes_updated += 1
            else:
                nodes_created += 1

            # Parse and sync edges
            parsed_edges = parse_edges(body)
            if parsed_edges or not force:  # always check edges for changed files
                ec, er = sync_edges_for_node(db, node.id, parsed_edges, warnings)
                edges_created_total += ec
                edges_removed_total += er

        # Detect deleted files
        nodes_deleted = delete_removed_files(db, synced_files)

        # Commit
        db.commit()

        sync_run.status = "completed"
        sync_run.completed_at = datetime.now(timezone.utc)
        sync_run.nodes_created = nodes_created
        sync_run.nodes_updated = nodes_updated
        sync_run.nodes_deleted = nodes_deleted
        sync_run.edges_created = edges_created_total
        sync_run.edges_removed = edges_removed_total
        sync_run.warnings_count = len(warnings)
        sync_run.errors_count = len(errors)
        db.flush()
        db.commit()

    except Exception as e:
        db.rollback()
        sync_run.status = "failed"
        sync_run.completed_at = datetime.now(timezone.utc)
        sync_run.error_message = str(e)
        db.flush()
        db.commit()

    return sync_run
