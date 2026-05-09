# Instagram Scraping Learnings (May 2026)

Condensed domain knowledge from building the IG Scraper Platform. Each learning is encoded as a graph edge so future agents don't repeat these discoveries.

## Instagram's Anti-Bot Evolution

- **`?__a=1&__d=1` JSON endpoint is now blocked** — Returns HTML instead of JSON. This changed May 2026. The profile spider was built assuming this endpoint worked; it failed on first real test.
- **`window._sharedData` extraction still works** — Instagram embeds user/profile data in a `<script>` tag on the public HTML page. Extractable via regex: `window\._sharedData\s*=\s*({.*?});\s*</script>`
- **`window.__INITIAL_STATE__` is the fallback** — When `_sharedData` isn't available, check for `__INITIAL_STATE__` which has a different data structure.
- **Login gate** — Instagram increasingly requires authentication even for public profiles. The `session_file` parameter on spiders supports cookie-based auth when needed.

## GraphQL Endpoints (for pagination)

- **Hashtag pagination uses GraphQL** — After the initial hashtag page, pagination goes through `instagram.com/graphql/query/` with `query_hash=9b498c08113f1e09617a1703c22b2f32`
- **Profile pagination uses `end_cursor`** — The `edge_owner_to_timeline_media.page_info.end_cursor` token enables scrolling through posts

## Rate Limiting Strategy

- **`DOWNLOAD_DELAY=3`** — Minimum delay between requests. Going below 2 seconds triggers aggressive rate limiting.
- **`CONCURRENT_REQUESTS=1`** — Never parallelize requests to Instagram. Single-threaded access is the only safe mode.
- **429 responses** — Instagram returns HTTP 429 when rate-limited. Scrapy's retry middleware handles this with exponential backoff.

## Data Structure Patterns

Instagram's JSON structure is deeply nested. Key extraction paths:

```
Profile:     graphql → user → {username, full_name, biography, 
              edge_followed_by.count, edge_follow.count,
              edge_owner_to_timeline_media.count, 
              edge_owner_to_timeline_media.edges[].node}

Hashtag:     graphql → hashtag → {edge_hashtag_to_media.count,
              edge_hashtag_to_top_posts.edges[].node}

Post:        node → {shortcode, edge_media_to_caption.edges[0].node.text,
              edge_media_preview_like.count, 
              edge_media_to_comment.count, taken_at_timestamp,
              is_video, display_url}
```

## Test Mode

Both spiders support `test_mode=True` which returns realistic mock data without hitting Instagram. Essential for:
- CI/CD pipelines
- Frontend development without real data
- Demonstrating the full pipeline without authentication
- `test_mode` parameter is consumed by the spider's `__init__` and checked in `start_requests`

## Graph Encoding

These domain learnings are encoded as concept nodes with `constrains` edges in the knowledge graph:

```
instagram-blocks-json-endpoint → constrains → profile-spider
instagram-rate-limiting        → constrains → scraper-execution
instagram-auth-required        → constrains → session-mgmt
multi-strategy-fallback        → enables    → scraper-builder
test-mode                      → enables    → pipeline-demo
```

Query to see all Instagram constraints:
```cypher
MATCH (c:concept)-[:constrains]->(r:requirement) 
WHERE id(c) =~ ".*instagram.*" OR id(c) =~ ".*scraper.*" 
RETURN c, r
```
