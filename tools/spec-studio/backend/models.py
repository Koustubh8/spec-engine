"""
SQLAlchemy ORM models for the Spec Graph.

data-model-spec:
  - polymorphic-nodes [SHALL]: single nodes table with kind discriminator
  - typed-directed-edges [SHALL]: edges table with from/to/predicate
  - graph-traversal-indexes [SHALL]: composite indexes for BFS
  - sync-compatibility [SHALL]: source_file + source_mtime
  - source-traceability [SHOULD]: sync_runs table
"""

import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    ForeignKey, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from database import Base


# ─── VALID KINDS ──────────────────────────────────────────────────────────────

VALID_NODE_KINDS = {
    "spec", "requirement", "scenario", "change", "design",
    "concept", "task", "tool", "person", "organization",
    "reference", "project",
}

VALID_STRENGTHS = {"SHALL", "MUST", "SHOULD", "MAY", "OPTIONAL"}

VALID_CHANGE_STATUSES = {"proposed", "exploring", "in-progress", "completed", "archived"}

VALID_SYNC_STATUSES = {"running", "completed", "failed"}


# ─── NODE TABLE ───────────────────────────────────────────────────────────────

class Node(Base):
    """
    Polymorphic node table. Single-table inheritance via `kind` discriminator.

    schema-model::
        nodes(id, slug, kind, title, body, metadata, tags,
              strength, status, source_file, source_mtime,
              created_at, updated_at)
    """

    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    kind = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=True, default="")

    # JSON metadata for frontmatter fields not captured as columns
    meta_json = Column("meta_json", Text, nullable=True, default="{}")

    # Tags stored as JSON array string (SQLite doesn't have native JSON arrays)
    tags = Column(Text, nullable=True, default="[]")

    # Requirement-specific
    strength = Column(String(20), nullable=True)

    # Change-specific
    status = Column(String(50), nullable=True, default="proposed")

    # Sync compatibility (data-model-spec: sync-compatibility)
    source_file = Column(String(500), nullable=True)
    source_mtime = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationships (bidirectional)
    outgoing_edges = relationship(
        "Edge", foreign_keys="Edge.from_node_id",
        back_populates="source_node", cascade="all, delete-orphan"
    )
    incoming_edges = relationship(
        "Edge", foreign_keys="Edge.to_node_id",
        back_populates="target_node", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Node {self.kind}:{self.slug}>"

    def to_dict(self, include_edges=False):
        """Serialize to dict for API responses."""
        d = {
            "id": self.id,
            "slug": self.slug,
            "kind": self.kind,
            "title": self.title,
            "body": self.body,
            "tags": self._parse_json(self.tags, []),
            "strength": self.strength,
            "status": self.status,
            "source_file": self.source_file,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_edges:
            d["outgoing_edges"] = [e.to_dict_with_nodes() for e in self.outgoing_edges]
            d["incoming_edges"] = [e.to_dict_with_nodes() for e in self.incoming_edges]
        return d

    @staticmethod
    def _parse_json(value, default=None):
        if not value:
            return default or []
        try:
            return json.loads(value) if isinstance(value, str) else value
        except (json.JSONDecodeError, TypeError):
            return default or []


# ─── EDGE TABLE ───────────────────────────────────────────────────────────────

class Edge(Base):
    """
    Typed directed edges between nodes.

    schema-model::
        edges(id, from_node_id, to_node_id, predicate, properties, created_at)
        UNIQUE(from_node_id, predicate, to_node_id)
    """

    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    predicate = Column(String(100), nullable=False)
    properties = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # ORM relationships
    source_node = relationship("Node", foreign_keys=[from_node_id], back_populates="outgoing_edges")
    target_node = relationship("Node", foreign_keys=[to_node_id], back_populates="incoming_edges")

    __table_args__ = (
        UniqueConstraint("from_node_id", "predicate", "to_node_id", name="uq_edge_unique"),
        # Graph traversal indexes (data-model-spec: graph-traversal-indexes)
        Index("idx_edges_from_predicate", "from_node_id", "predicate"),
        Index("idx_edges_to_predicate", "to_node_id", "predicate"),
    )

    def __repr__(self):
        return f"<Edge {self.from_node_id} -[{self.predicate}]-> {self.to_node_id}>"

    def to_dict(self):
        """Serialize to dict for API responses."""
        return {
            "id": self.id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "predicate": self.predicate,
            "properties": json.loads(self.properties) if self.properties else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_dict_with_nodes(self):
        """Serialize with source/target node slugs and titles."""
        d = self.to_dict()
        if self.source_node:
            d["from_slug"] = self.source_node.slug
            d["from_title"] = self.source_node.title
            d["from_kind"] = self.source_node.kind
        if self.target_node:
            d["to_slug"] = self.target_node.slug
            d["to_title"] = self.target_node.title
            d["to_kind"] = self.target_node.kind
        return d


# ─── SYNC RUNS TABLE ──────────────────────────────────────────────────────────

class SyncRun(Base):
    """
    Tracks sync operations for audit trail.

    data-model-spec: source-traceability [SHOULD]
    sync-engine-spec: sync-run-logging [SHOULD]
    """

    __tablename__ = "sync_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="running")
    nodes_created = Column(Integer, default=0)
    nodes_updated = Column(Integer, default=0)
    nodes_deleted = Column(Integer, default=0)
    edges_created = Column(Integer, default=0)
    edges_removed = Column(Integer, default=0)
    warnings_count = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "nodes_created": self.nodes_created,
            "nodes_updated": self.nodes_updated,
            "nodes_deleted": self.nodes_deleted,
            "edges_created": self.edges_created,
            "edges_removed": self.edges_removed,
            "warnings_count": self.warnings_count,
            "errors_count": self.errors_count,
            "error_message": self.error_message,
        }
