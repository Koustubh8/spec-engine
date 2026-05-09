# Domain Patterns Learned from Candle CRM (May 2026)

Patterns discovered during user-informed exploration for a candle influencer CRM.
Each pattern is a first-class `concept` node in the knowledge graph with `is_a → reusable-pattern`.
Before building any new CRM-like application, query these patterns.

## IG Handle as Primary Customer Key

**Why it emerged:** The user said orders come through Instagram DMs. The IG handle is
the natural customer identifier — it's unique, it's how the user thinks about customers,
and it's what appears in every DM.

**Graph encoding:**
```
ig-handle-as-primary-key → is_a → reusable-pattern
candle-crm-v2 → reuses → ig-handle-as-primary-key

dm-order-channel → constrains → customer-mgmt
ig-handle-as-primary-key → constrains → customer-mgmt
```

**What it means for code generation:**
- Customer API must support lookup by `ig_handle` (not just by name or ID)
- The quick-order flow must accept `@handle` and auto-detect existing customers
- Duplicate IG handle detection (return existing customer if handle matches)
- Customer list sorted by `order_count` (repeat buyers surface first)

## 3-State Payment Flow

**Why it emerged:** The user accepts UPI payments with screenshot verification.
The payment lifecycle has three states, not two:

```
unpaid → verifying → paid
   ↑        │          │
   └────────┴──────────┘  (can revert from any state)
```

**Graph encoding:**
```
three-state-payment-flow → is_a → reusable-pattern
payment-upi-screenshot → constrains → payment-tracking
```

**What it means for code generation:**
- Payment status is not a boolean — it's an enum with 3 values
- Transition to "verifying" requires a `payment_ref` field (UPI reference/screenshot details)
- Dashboard must highlight both "unpaid" AND "verifying" orders (not just "unpaid")
- Payment toggle button cycles: unpaid → verifying → paid → unpaid

## Dashboard as Pending-Item Triage Center

**Why it emerged:** The user's #1 pain point was "DMs get buried, I lose track of pending orders."
The dashboard isn't a stats page — it's a triage center for pending work.

**Graph encoding:**
```
dashboard-as-triage → is_a → reusable-pattern
core-pain-buried-dms → constrains → order-tracking
volume-20-50 → constrains → order-tracking  (speed is critical)
```

**What it means for code generation:**
- Dashboard shows pending items FIRST, with action buttons on each row
- Stats are secondary (small cards at top)
- Every pending row has visible action buttons (confirm, dispatch, payment)
- Quick-order bar is always visible on dashboard (not buried in a separate tab)
- Designed for <10 second order entry from DM to system

## FastAPI + SQLite CRUD Template

**Why it emerged:** Both IG Scraper and Candle CRM use the same stack pattern:
FastAPI with SQLite, dark theme HTML frontend, TestClient for verification.

**Graph encoding:**
```
fastapi-sqlite-crud → is_a → reusable-pattern
candle-crm-v2 → reuses → fastapi-sqlite-crud
```

**What it means for code generation:**
- Backend follows a standard pattern: `def db()` for connection, `conn.row_factory = sqlite3.Row`
- All tables have `id TEXT PRIMARY KEY` (UUID truncated to 8 chars)
- Frontend is a single `index.html` with vanilla JS, dark CSS theme, modal-based forms
- Server port convention: 8080 (ig-scraper), 8081 (candle-crm), etc.

## SQLite Schema Evolution Pitfall

**Why it emerged:** `CREATE TABLE IF NOT EXISTS` doesn't update existing tables.
When v2 of the CRM added columns, the old DB schema caused `sqlite3.OperationalError`.

**Mitigation:** Delete the DB file during development when schema changes.
For production, add migration logic. The graph encodes this as a pitfall pattern.

## Modal-Based Quick Actions

**Why it emerged:** 20-50 orders/day requires speed. Multi-page forms are too slow.
Modal overlays allow quick actions without leaving the current view.

**What it means for code generation:**
- Forms open in modals, not page navigations
- "Quick" actions (order, message, payment) are single-modal operations
- Modal content is dynamically generated from API data (product dropdowns, customer lookup)

## User-Involved Exploration (Meta-Pattern)

**Why it emerged:** The v1 CRM was built from assumptions. The v2 CRM was rebuilt
after 6 clarify questions revealed the real workflow. The difference was dramatic.

**Graph encoding:**
```
explore-before-spec → is_a → reusable-pattern
agent-forgets-graph-updates → constrains → explore-before-spec
```

**Enforcement:**
- `EXPLORATION_GATE` lint rule: change must have findings before archive
- `GRAPH_UPDATE_CHECKPOINT` lint rule: exploration-tagged changes must have findings
- `GRAPH_INVENTORY_CHECK` lint rule: new specs should reference reusable patterns
- `REUSE_CHECK` lint rule: exploration must query reusable-pattern before proposing

## Candle CRM v2 — Complete Reuse Map

```
candle-crm-v2
  ├── reuses → ig-handle-as-primary-key       (DM-based customer identification)
  ├── reuses → three-state-payment-flow        (UPI screenshot verification)
  ├── reuses → dashboard-as-triage             (pending orders first)
  ├── reuses → fastapi-sqlite-crud             (backend template)
  ├── reuses → dark-dashboard                  (frontend template)
  └── reuses → modal-quick-action              (speed-optimized UX)
```

Any future CRM-like application should start by querying `reusable-pattern` and reading this file.
