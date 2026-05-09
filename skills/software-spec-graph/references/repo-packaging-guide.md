# Repository Packaging Guide

How to package the spec-graph methodology as a professional, shareable GitHub repository.

## Repository Structure

```
spec-engine/
├── README.md              # Landing page with mission, quick start, table of contents
├── CONTRIBUTING.md        # How to contribute specs and tools
├── LICENSE                # MIT
├── .gitignore
│
├── standards/             # The rules of the system
│   ├── predicate-vocabulary.md  # All predicates with directions and inverses
│   ├── node-kinds.md            # Node type definitions
│   ├── lifecycle.md             # 8-phase spec lifecycle
│   └── naming-conventions.md    # Slug naming, file organization
│
├── templates/             # Reusable node templates
│   ├── spec-node.md
│   ├── requirement-node.md
│   ├── scenario-node.md
│   └── change-node.md
│
├── guides/                # How-to documentation
│   ├── getting-started.md
│   └── how-to-spec-a-project.md
│
├── tools/                 # Implementation
│   ├── knowledge-graph/   # Python scripts (ingest, query, lint)
│   ├── spec-studio/       # Web dashboard (FastAPI + React)
│   └── nebula/            # NebulaGraph Docker + sync scripts
│
└── examples/              # Worked examples
    ├── hello-spec/        # Minimal demo
    └── spec-studio/       # The dashboard that specs itself
```

## What to Include

### Required (for anyone to adopt the methodology)
- `standards/` — the predicate vocabulary and lifecycle are the core reference
- `templates/` — without templates, new users don't know how to write a spec node
- `tools/knowledge-graph/` — the ingest, query, lint scripts are the entry point
- `README.md` — must include a quick start that works in 3 commands

### Recommended (for team adoption)
- `guides/` — step-by-step walkthroughs reduce onboarding friction
- `examples/` — worked examples show the methodology in practice
- `CONTRIBUTING.md` — sets expectations for spec PRs

### Optional (for advanced setups)
- `tools/spec-studio/` — the web dashboard (useful once the KG has 50+ nodes)
- `tools/nebula/` — NebulaGraph integration (useful at enterprise scale)

## What NOT to Include

- **Personal information** — no personal belief systems, philosophy, hardware specs, personal preferences, or individual behavioral data. The repo should be adoptable by anyone without context about the author.
- **Bureaucratic overhead** — avoid heavy governance documents (approval matrices, voting processes, change advisory boards) unless the methodology is used across multiple teams. For individual or small-team adoption, keep it lean.
- **Over-branding** — labels like "Center of Excellence", "Enterprise Framework", "Certified Methodology" create adoption friction. Let the methodology speak for itself.
- **Unrelated domain content** — don't include domain-specific examples (marketing, finance, healthcare) unless they're the focus of the repo. Generic examples are more useful to more people.
- **Incomplete projects** — half-finished specs or partial implementations confuse new readers. Either complete them or remove them.

## README Tone

The README sets the tone for the project:
- **Professional but approachable** — explain what the methodology does and why it matters, but avoid corporate jargon
- **Quick value** — the first thing a reader sees should be "what can I do with this?" not "what committee approved this?"
- **Concrete over abstract** — show command examples, not architecture diagrams
- **Minimal prerequisites** — assume nothing about the reader's context

## Key Decisions

### License
MIT is the default. It maximizes adoption and contribution.

### File naming
- Slugs are kebab-case: `user-authentication.md`, not `userAuthentication.md` or `User Authentication.md`
- Directory names are plural: `specs/`, `requirements/`, `concepts/`

### Edge declarations
Use `|rel:PREDICATE| [[KIND/SLUG]]` syntax consistently. Every edge file should be parseable by the `ingest.py` regex.

## When to Publish

Publish to GitHub when:
- The standards document is complete enough for someone to write a spec without asking questions
- At least one project has been fully spec'd as an example
- The ingest + query + lint scripts work end-to-end
- You would be comfortable sending the link to a stranger
