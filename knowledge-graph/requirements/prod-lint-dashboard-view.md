---
title: Production Lint Dashboard View
kind: requirement
created: 2026-05-10
updated: 2026-05-10
tags: [ui, dashboard, lint]
strength: SHOULD
---

# Production Lint Dashboard View

The dashboard SHOULD display a production readiness card showing the lint score and a breakdown of passing/failing rules.

Layout:
- Score ring/circle (color-coded: green/orange/red)
- Rule list grouped by severity (errors first, then warnings)
- Each rule shows: pass/fail icon, name, message, suggestion text
- Quick-fix suggestions: "Add logging config" or "Define timeout" that could link to spec creation

The card SHOULD be auto-expanded by default if any rules fail.

|rel:portion_of| [[specs/prod-readiness-linter]]
|rel:touches| [[tools/react-frontend]]
