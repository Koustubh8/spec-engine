"""
Production Readiness Linter

Runs 12 production-readiness checks against a spec graph stored in SQLAlchemy.
Each rule queries the DB for specific edge/node patterns that indicate
whether a component is production-ready.

prod-readiness-linter: prod-lint-rules [SHALL]
"""

import sys
import os
from sqlalchemy import func
from sqlalchemy.orm import Session

# Ensure backend/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from models import Node, Edge, SyncRun


# ─── RULE DEFINITIONS ─────────────────────────────────────────────────────────

def rule_logging_specified(db: Session):
    """P1: Every exposed endpoint has a logging reference."""
    specs_with_endpoints = (
        db.query(Edge)
        .filter(Edge.predicate == "exposes")
        .all()
    )
    if not specs_with_endpoints:
        return True, None

    # Check if any node references logging, loguru, structlog, etc.
    logging_refs = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "tool", "reference"]),
            Node.slug.ilike("%log%")
        )
        .count()
    )
    if logging_refs > 0:
        return True, None
    return False, "No logging framework reference found. Add a 'logging' or 'loguru' concept node."


def rule_error_handling_specified(db: Session):
    """P2: Every fails_with condition has an error handler spec."""
    fails_with_edges = (
        db.query(Edge)
        .filter(Edge.predicate == "fails_with")
        .count()
    )
    error_handler_concepts = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "spec"]),
            Node.slug.ilike("%error%handler%")
        )
        .count()
    )
    if fails_with_edges == 0:
        return True, None  # No fail conditions = nothing to handle
    if error_handler_concepts > 0:
        return True, None
    return False, f"{fails_with_edges} `fails_with` edges exist but no error handler spec found."


def rule_input_validation_specified(db: Session):
    """P3: Endpoints with accepts have a schema/reference."""
    accepts_edges = (
        db.query(Edge)
        .filter(Edge.predicate == "accepts")
        .count()
    )
    schema_refs = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "reference"]),
            Node.slug.ilike("%schema%") | Node.slug.ilike("%pydantic%") | Node.slug.ilike("%valid%")
        )
        .count()
    )
    if accepts_edges == 0:
        return True, None
    if schema_refs > 0:
        return True, None
    return False, "Endpoints declare `accepts` but no schema/Pydantic model reference found."


def rule_health_endpoint_specified(db: Session):
    """P4: Has at least one health/readyz endpoint exposed."""
    health_nodes = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "spec"]),
            Node.slug.ilike("%health%") | Node.slug.ilike("%readyz%")
        )
        .count()
    )
    if health_nodes > 0:
        return True, None
    return False, "No health check endpoint found. Add a GET /health or GET /readyz spec."


def rule_cors_configured(db: Session):
    """P5: API spec references CORS or allowed origins."""
    cors_nodes = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "reference"]),
            Node.slug.ilike("%cors%") | Node.slug.ilike("%origin%")
        )
        .count()
    )
    if cors_nodes > 0:
        return True, None
    return False, "No CORS configuration found. Add a `cors` concept node to API spec."


def rule_timeout_specified(db: Session):
    """P6: Long-running operations have timeout specs."""
    long_running = (
        db.query(Edge)
        .filter(
            Edge.predicate.in_(["exposes", "triggers"]),
        )
        .all()
    )
    timeout_refs = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "requirement"]),
            Node.slug.ilike("%timeout%")
        )
        .count()
    )
    if timeout_refs > 0:
        return True, None
    if len(long_running) == 0:
        return True, None
    return False, f"{len(long_running)} endpoints exist but no timeout specification found."


def rule_retry_specified(db: Session):
    """P7: External service calls have retry strategy."""
    external_deps = (
        db.query(Edge)
        .filter(Edge.predicate == "depends_on")
        .count()
    )
    retry_refs = (
        db.query(Node)
        .filter(
            Node.slug.ilike("%retry%")
        )
        .count()
    )
    if external_deps == 0:
        return True, None
    if retry_refs > 0:
        return True, None
    return False, f"{external_deps} `depends_on` edges exist but no retry strategy found."


def rule_config_externalized(db: Session):
    """P8: Configuration is externalized (env vars, config files)."""
    config_refs = (
        db.query(Node)
        .filter(
            Node.kind.in_(["concept", "reference"]),
            Node.slug.ilike("%env%var%") | Node.slug.ilike("%config%") | Node.slug.ilike("%dotenv%") | Node.slug.ilike("%settings%")
        )
        .count()
    )
    if config_refs > 0:
        return True, None
    return False, "No configuration externalization found. Add `.env` or `settings` reference."


def rule_migration_strategy(db: Session):
    """P9: DB schema changes have a migration tool reference."""
    # Check for Alembic or migration reference
    migration_refs = (
        db.query(Node)
        .filter(
            Node.slug.ilike("%alembic%") | Node.slug.ilike("%migration%")
        )
        .count()
    )
    has_db_specs = (
        db.query(Node)
        .filter(
            Node.kind == "spec",
            Node.slug.ilike("%data%model%") | Node.slug.ilike("%db%") | Node.slug.ilike("%schema%")
        )
        .count()
    )
    if not has_db_specs:
        return True, None  # No DB = no migration needed
    if migration_refs > 0:
        return True, None
    return False, "DB schema spec exists but no migration tool (Alembic) referenced."


def rule_environments_defined(db: Session):
    """P10: Spec deploys to multiple environments (dev/staging/prod)."""
    deploy_edges = (
        db.query(Edge)
        .filter(Edge.predicate == "deploys_to")
        .count()
    )
    if deploy_edges >= 2:
        return True, None
    if deploy_edges == 0:
        return False, "No `deploys_to` edges found. Define at least dev and production targets."
    return False, "Only 1 deployment target found. Add staging or production deployment spec."


def rule_monitoring_specified(db: Session):
    """P11: Service has monitoring/metrics reference."""
    monitoring_refs = (
        db.query(Node)
        .filter(
            Node.slug.ilike("%monitor%") | Node.slug.ilike("%metric%") | Node.slug.ilike("%prometheus%") | Node.slug.ilike("%grafana%") | Node.slug.ilike("%observability%")
        )
        .count()
    )
    if monitoring_refs > 0:
        return True, None
    return False, "No monitoring/metrics reference. Add `prometheus`, `grafana`, or `observability` concept."


def rule_ci_configured(db: Session):
    """P12: Project has CI configuration."""
    ci_refs = (
        db.query(Node)
        .filter(
            Node.slug.ilike("%ci%") | Node.slug.ilike("%github%action%") | Node.slug.ilike("%gitlab%ci%") | Node.slug.ilike("%circleci%") | Node.slug.ilike("%jenkins%")
        )
        .count()
    )
    if ci_refs > 0:
        return True, None
    return False, "No CI configuration found. Add `github-actions` or CI concept node."


# ─── LINTER ENGINE ────────────────────────────────────────────────────────────

RULES = [
    {"name": "LOGGING_SPECIFIED",      "severity": "warning", "check": rule_logging_specified,          "description": "Every exposed endpoint has logging"},
    {"name": "ERROR_HANDLING_SPECIFIED","severity": "error",   "check": rule_error_handling_specified,    "description": "fails_with conditions have error handlers"},
    {"name": "INPUT_VALIDATION_SPECIFIED","severity": "warning","check": rule_input_validation_specified, "description": "accepts endpoints have schema/models"},
    {"name": "HEALTH_ENDPOINT_SPECIFIED","severity": "warning", "check": rule_health_endpoint_specified,  "description": "Service has /health or /readyz"},
    {"name": "CORS_CONFIGURED",         "severity": "warning", "check": rule_cors_configured,             "description": "API has CORS configuration"},
    {"name": "TIMEOUT_SPECIFIED",       "severity": "warning", "check": rule_timeout_specified,           "description": "Long-running ops have timeout specs"},
    {"name": "RETRY_SPECIFIED",         "severity": "warning", "check": rule_retry_specified,             "description": "External calls have retry strategy"},
    {"name": "CONFIG_EXTERNALIZED",     "severity": "warning", "check": rule_config_externalized,         "description": "Config uses env vars, not hardcoding"},
    {"name": "MIGRATION_STRATEGY",      "severity": "warning", "check": rule_migration_strategy,          "description": "DB changes have migration tool"},
    {"name": "ENVIRONMENTS_DEFINED",    "severity": "warning", "check": rule_environments_defined,        "description": "Defines dev/staging/prod targets"},
    {"name": "MONITORING_SPECIFIED",    "severity": "warning", "check": rule_monitoring_specified,        "description": "Service has monitoring/metrics"},
    {"name": "CI_CONFIGURED",           "severity": "warning", "check": rule_ci_configured,               "description": "Project has CI pipeline"},
]


def run_prod_lint(db: Session):
    """Run all 12 production readiness rules against the database.
    
    Returns dict with score, max_score, status, and rules results.
    """
    results = []
    passed_count = 0

    for rule in RULES:
        try:
            passed, message = rule["check"](db)
        except Exception as e:
            passed = False
            message = f"Lint check error: {e}"

        result = {
            "name": rule["name"],
            "passed": passed,
            "severity": rule["severity"],
            "description": rule["description"],
            "message": message,
        }
        results.append(result)
        if passed:
            passed_count += 1

    score = passed_count
    max_score = len(RULES)

    # Determine overall status
    errors_failing = [r for r in results if not r["passed"] and r["severity"] == "error"]
    if errors_failing:
        status = "failed"
    elif score < max_score:
        status = "warning"
    else:
        status = "passed"

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "rules": results,
    }


def print_report(report: dict):
    """Pretty-print the lint report to terminal."""
    score = report["score"]
    max_score = report["max_score"]
    status = report["status"]

    if status == "passed":
        icon = "🟢"
    elif status == "warning":
        icon = "🟡"
    else:
        icon = "🔴"

    print(f"\n{'='*60}")
    print(f"  PRODUCTION READINESS: {score}/{max_score} {icon}")
    print(f"{'='*60}")
    print()

    errors = [r for r in report["rules"] if not r["passed"] and r["severity"] == "error"]
    warnings = [r for r in report["rules"] if not r["passed"] and r["severity"] == "warning"]
    passing = [r for r in report["rules"] if r["passed"]]

    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for r in errors:
            print(f"    ❌ {r['name']} — {r['message'] or r['description']}")
        print()

    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for r in warnings:
            print(f"    ⚠️  {r['name']} — {r['message'] or r['description']}")
        print()

    if passing:
        print(f"  PASSING ({len(passing)}):")
        for r in passing:
            print(f"    ✅ {r['name']}")

    print()


if __name__ == "__main__":
    """CLI usage: python3 prod_lint.py [--db PATH]"""
    import argparse
    parser = argparse.ArgumentParser(description="Production Readiness Linter")
    parser.add_argument("--db", help="Path to SQLite database (default: ../backend/spec_studio.db)")
    args = parser.parse_args()

    db_path = args.db or os.path.join(os.path.dirname(__file__), "..", "backend", "spec_studio.db")
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        print("Run the sync first: cd backend && python3 -c 'from sync import run_sync; ...'")
        sys.exit(1)

    # Set DB path for database.py
    os.environ["SPEC_STUDIO_DB"] = db_path

    from database import SessionLocal
    db = SessionLocal()
    try:
        report = run_prod_lint(db)
        print_report(report)
    finally:
        db.close()
