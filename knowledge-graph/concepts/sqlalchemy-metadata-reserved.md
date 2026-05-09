---
title: SQLAlchemy metadata Is Reserved
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [learning, sqlalchemy, pitfall]
---

# SQLAlchemy metadata Is Reserved

The column name `metadata` conflicts with `Base.metadata` in SQLAlchemy's declarative base. Any model class using `metadata` as a column name raises `InvalidRequestError: Attribute name 'metadata' is reserved`.

Fix: rename the column. Use `meta_json` with explicit column name via `Column("meta_json", Text)`.

Applies to: any SQLAlchemy model where you need a generic JSON metadata field.
|rel:added_by| [[changes/explore-spec-studio]]
|rel:constrains| [[requirements/polymorphic-nodes]]
