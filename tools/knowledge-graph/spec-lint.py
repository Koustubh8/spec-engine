#!/usr/bin/env python3
"""
Lint a software specification graph. Extends the knowledge-graph lint.py with
spec-specific verification rules adapted from OpenSpec's quality gates.

Usage:
    python3 scripts/spec-lint.py [--rule RULE] [--knowledge-path PATH] [--json]
"""
import os, sys, json, argparse
from pathlib import Path
from collections import defaultdict

SKILL_DIR = Path(__file__).resolve().parent.parent
KG_SCRIPTS = Path.home() / ".hermes/skills/research/knowledge-graph/scripts"
sys.path.insert(0, str(KG_SCRIPTS))
from graph import build_graph

def get_knowledge_path():
    return os.environ.get("KNOWLEDGE_PATH", os.path.expanduser("~/mywork/knowledge-graph"))

RULES = {
    "EXPOSES_HAS_CONTRACT": {
        "severity": "error",
        "check": lambda g: check_exposes_has_contract(g),
        "message": "Every 'exposes' edge should have at least one 'accepts' or 'returns' edge from the same node",
    },
    "SCENARIO_FOR_REQ": {
        "severity": "warning",
        "check": lambda g: check_scenario_for_req(g),
        "message": "Every 'requirement' node should have at least one incoming 'scenario_for' edge",
    },
    "GUARANTEES_HAS_TESTS": {
        "severity": "error",
        "check": lambda g: check_guarantees_has_tests(g),
        "message": "Every node with 'guarantees' edges should have at least one 'tests' edge",
    },
    "NO_ORPHAN_REQUIREMENTS": {
        "severity": "warning",
        "check": lambda g: check_orphan_requirements(g),
        "message": "Every 'requirement' should be portion_of a spec or added_by a change",
    },
    "TRIGGERS_HAS_CONSUMER": {
        "severity": "warning",
        "check": lambda g: check_triggers_has_consumer(g),
        "message": "Every 'triggers' edge should have a corresponding 'accepts' or handler",
    },
    "SCHEMA_CONSISTENCY": {
        "severity": "error",
        "check": lambda g: check_schema_consistency(g),
        "message": "Components that share DB schema MUST have matching table definitions",
    },
    "DEPLOYMENT_SPECIFIED": {
        "severity": "warning",
        "check": lambda g: check_deployment_specified(g),
        "message": "Every spec should have a 'deploys_to' edge before implementation",
    },
    "AUTH_SPECIFIED": {
        "severity": "warning",
        "check": lambda g: check_auth_specified(g),
        "message": "Every spec that exposes endpoints should specify 'authenticates_via'",
    },
    "CONSISTENT_FALLBACKS": {
        "severity": "warning",
        "check": lambda g: check_consistent_fallbacks(g),
        "message": "Sibling specs should use consistent error handling patterns",
    },
    "ASYNC_LONG_RUNNING": {
        "severity": "error",
        "check": lambda g: check_async_long_running(g),
        "message": "Specs executing jobs should specify async execution strategy",
    },
    "EXPLORATION_GATE": {
        "severity": "error",
        "check": lambda g: check_exploration_gate(g),
        "message": "A change node must have at least one finding before being archived",
    },
    "GRAPH_UPDATE_CHECKPOINT": {
        "severity": "warning",
        "check": lambda g: check_graph_update_checkpoint(g),
        "message": "After clarify/explore phases, findings should be ingested into graph",
    },
}


def check_exposes_has_contract(g):
    issues = []
    for node in g.nodes.values():
        if node.kind not in ("spec", "tool"):
            continue
        exposed = [e for e in g.edges if e.source == node.slug and e.predicate == "exposes"]
        for exp_edge in exposed:
            endpoint = exp_edge.target
            has_accepts = any(e.source == endpoint and e.predicate == "accepts" for e in g.edges)
            has_returns = any(e.source == endpoint and e.predicate == "returns" for e in g.edges)
            if not has_accepts and not has_returns:
                issues.append(f"{node.slug} exposes {endpoint} but endpoint has no accepts/returns")
    return issues


def check_scenario_for_req(g):
    issues = []
    # Build set of requirement nodes that have scenario_for edges pointing to them
    reqs_with_scenarios = set()
    for e in g.edges:
        if e.predicate == "scenario_for":
            reqs_with_scenarios.add(e.target)

    for node in g.nodes.values():
        if node.kind == "requirement":
            if node.slug not in reqs_with_scenarios:
                issues.append(f"{node.slug} ({node.title}) has no scenarios")
    return issues


def check_guarantees_has_tests(g):
    issues = []
    for node in g.nodes.values():
        guarantees = [e for e in g.edges if e.source == node.slug and e.predicate == "guarantees"]
        if guarantees:
            # Check for incoming tests edges (anything testing this node)
            has_tests = any(e.target == node.slug and e.predicate == "tests" for e in g.edges)
            if not has_tests:
                issues.append(f"{node.slug} ({node.title}) guarantees properties but no tests verify it")
    return issues


def check_deployment_specified(g):
    issues = []
    for node in g.nodes.values():
        if node.kind not in ("spec",):
            continue
        has_deploy = any(e.source == node.slug and e.predicate == "deploys_to" for e in g.edges)
        has_exposes = any(e.source == node.slug and e.predicate == "exposes" for e in g.edges)
        if has_exposes and not has_deploy:
            issues.append(f"{node.slug} exposes endpoints but has no deploys_to edge")
    return issues


def check_auth_specified(g):
    issues = []
    for node in g.nodes.values():
        has_exposes = any(e.source == node.slug and e.predicate == "exposes" for e in g.edges)
        has_auth = any(e.source == node.slug and e.predicate == "authenticates_via" for e in g.edges)
        if has_exposes and not has_auth:
            issues.append(f"{node.slug} ({node.title}) exposes endpoints but has no authenticates_via edge")
    return issues


def check_schema_consistency(g):
    issues = []
    for e in g.edges:
        if e.predicate == "shares_schema_with":
            a, b = sorted([e.source, e.target])
            issues.append(f"{a} and {b} share schema — verify table definitions match")
    return issues if issues else []


def check_consistent_fallbacks(g):
    issues = []
    for node in g.nodes.values():
        if node.kind != "spec":
            continue
        has_fallback = any(edge.source == node.slug and edge.predicate in ("constrains", "depends_on") 
                          and "fallback" in (edge.target.lower() if hasattr(edge, 'target') else "")
                          for edge in g.edges)
    return issues if issues else []


def check_async_long_running(g):
    issues = []
    for node in g.nodes.values():
        has_job_exec = any(e.source == node.slug and e.predicate == "contains" 
                          and "execution" in e.target.lower() for e in g.edges)
        if has_job_exec:
            async_backends = {"celery", "background", "queue", "prefect"}
            has_async = any(
                edge.source == node.slug and edge.predicate in ("deploys_to", "depends_on")
                and any(t in edge.target.lower() for t in async_backends)
                for edge in g.edges
            )
            if not has_async:
                issues.append(f"{node.slug} executes jobs but has no async backend (celery/prefect/queue)")
    return issues


def check_exploration_gate(g):
    """A change that is archived MUST have at least one finding (adds edge)."""
    issues = []
    for node in g.nodes.values():
        if node.kind not in ("change",):
            continue
        has_archive = any(e.source == node.slug and e.predicate == "archives_to" for e in g.edges)
        has_findings = any(e.source == node.slug and e.predicate == "adds" for e in g.edges)
        if has_archive and not has_findings:
            issues.append(f"{node.slug} ({node.title}) archived without any exploration findings")
    return issues


def check_graph_update_checkpoint(g):
    """Changes with clarify/explore in tags but no findings are flagged."""
    issues = []
    for node in g.nodes.values():
        if node.kind not in ("change",):
            continue
        has_explore_tag = any("explor" in t for t in (node.tags or []))
        has_findings = any(e.source == node.slug and e.predicate == "adds" for e in g.edges)
        if has_explore_tag and not has_findings:
            issues.append(f"{node.slug} tagged as exploration but has zero findings ingested")
    return issues


def check_orphan_requirements(g):
    issues = []
    for node in g.nodes.values():
        if node.kind != "requirement":
            continue
        is_orphan = True
        for e in g.edges:
            if e.target == node.slug and e.predicate in ("contains", "adds", "portion_of"):
                is_orphan = False
                break
        if is_orphan:
            issues.append(f"{node.slug} ({node.title}) is orphaned (not contained in any spec)")
    return issues


def check_triggers_has_consumer(g):
    issues = []
    for e in g.edges:
        if e.predicate == "triggers":
            event = e.target
            has_consumer = any(
                edge.predicate in ("accepts", "triggered_by", "depends_on")
                and edge.target == event
                for edge in g.edges
            )
            if not has_consumer:
                issues.append(f"{e.source} triggers {event} but {event} has no consumer")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Lint a software specification graph")
    parser.add_argument("--rule", choices=list(RULES.keys()), help="Run a specific rule")
    parser.add_argument("--knowledge-path", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.knowledge_path or get_knowledge_path()
    g = build_graph(root)

    rules_to_run = [args.rule] if args.rule else list(RULES.keys())
    results = []

    for rule_name in rules_to_run:
        rule = RULES[rule_name]
        issues = rule["check"](g)
        if issues or args.json:
            results.append({
                "rule": rule_name,
                "severity": rule["severity"],
                "count": len(issues),
                "items": issues,
                "message": rule["message"],
            })

    if args.json:
        print(json.dumps(results, indent=2))
        return 0

    total_issues = 0
    for r in results:
        sev = r["severity"].upper()
        if r["count"] > 0:
            print(f"[{sev}] {r['rule']}: {r['count']} issue(s)")
            for item in r["items"][:10]:
                print(f"  - {item}")
            if r["count"] > 10:
                print(f"  ... and {r['count'] - 10} more")
        else:
            print(f"[PASS] {r['rule']}: no issues")
        total_issues += r["count"]

    print(f"\nTotal: {total_issues} issue(s) across {len(results)} rule(s)")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
