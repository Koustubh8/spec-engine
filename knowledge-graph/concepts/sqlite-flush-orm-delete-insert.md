---
title: SQLite Flush Race in ORM Delete-then-Insert
kind: concept
created: 2026-05-10
updated: 2026-05-10
tags: [learning, sqlite, sqlalchemy]
---

# SQLite Flush Race in ORM Delete-then-Insert

Within the same SQLite transaction, `db.query(Model).filter(...).all()` + `db.delete(obj)` + `db.flush()` followed by `db.add(new_obj)` + `db.flush()` doesn't reliably commit the DELETE before the INSERT hits UNIQUE constraints. The ORM's identity map and SQLite's deferred constraint checking can cause the INSERT to see the deleted rows as still present.

Fix: use bulk SQL execution for the DELETE phase:
```python
from sqlalchemy import text as sa_text
db.execute(sa_text("DELETE FROM edges WHERE from_node_id = :nid"), {"nid": node_id})
db.flush()
```

Then use the ORM for INSERTs as normal.
|rel:added_by| [[changes/explore-spec-studio]]
|rel:constrains| [[requirements/edge-reconciliation]]
