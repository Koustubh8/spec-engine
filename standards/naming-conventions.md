# Naming Conventions

Consistent naming enables predictable queries and reliable auto-ingestion.

## Slug Format

All node files use **lower-kebab-case** slugs:

```
Good:
  user-authentication.md
  api-layer-spec.md
  dm-order-channel.md

Bad:
  UserAuthentication.md
  API-Layer.md
  DMOrderChannel.md
```

The slug should match the node title in lowercase with hyphens.

## Directory Names

Directories are always **plural**:

```
specs/           # NOT spec/
requirements/    # NOT requirement/
scenarios/
changes/         # (not deltas/ — that's the NebulaGraph tag)
concepts/
designs/
tasks/
tools/
people/
organizations/
projects/
references/
```

## File Location by Kind

| Node Kind | Directory |
|-----------|-----------|
| spec | `specs/` |
| requirement | `requirements/` |
| scenario | `scenarios/` |
| change | `changes/` |
| design | `designs/` |
| concept | `concepts/` |
| task | `tasks/` |
| tool | `tools/` |
| person | `people/` |
| organization | `organizations/` |
| project | `projects/` |
| reference | `references/` |

## Edge Declaration Format

Edges are declared in markdown with the pipe-link syntax:

```
|rel:PREDICATE| [[KIND/SLUG]]
```

- `PREDICATE` — lowercase with underscores (e.g., `spec_of`, `change_for`)
- `KIND/SLUG` — the directory name and file slug of the target node

Examples:
```
|rel:exposes| [[concepts/post-login]]
|rel:contains| [[requirements/user-auth]]
|rel:spec_of| [[tools/auth-module]]
|rel:scenario_for| [[requirements/user-auth]]
```

## Tag Format

Tags in YAML frontmatter are lowercase, hyphenated:

```yaml
tags: [auth, security, mfa]
```

Numeric tags must be quoted to prevent YAML parsing as integers:

```yaml
tags: [monastic, belur-math, '1898']
```

## Frontmatter Fields

All nodes must include:
- `title` — human-readable name
- `kind` — singular kind name (concept, spec, requirement, etc.)
- `created` — ISO date (YYYY-MM-DD)
- `updated` — ISO date (YYYY-MM-DD)

Optional:
- `tags` — array of lowercase keywords
- `status` — for change nodes: proposed, in_progress, archived
- `strength` — for requirement nodes: SHALL, MUST, SHOULD, MAY
