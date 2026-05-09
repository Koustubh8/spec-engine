const API_BASE = '/api';  // Vite proxies /api to backend

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API ${res.status}: ${err}`);
  }
  return res.json();
}

export async function getStats() {
  return fetchJSON('/stats');
}

export async function listNodes(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return fetchJSON(`/nodes?${qs}`);
}

export async function getNode(slug) {
  return fetchJSON(`/nodes/${encodeURIComponent(slug)}`);
}

export async function listEdges(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return fetchJSON(`/edges?${qs}`);
}

export async function traverseGraph(seed, depth = 3, predicates = null, direction = 'forward') {
  return fetchJSON('/query/traverse', {
    method: 'POST',
    body: JSON.stringify({ seed, depth, predicates, direction }),
  });
}

export async function findPath(from, to, maxDepth = 10) {
  return fetchJSON('/query/path', {
    method: 'POST',
    body: JSON.stringify({ from_node: from, to_node: to, max_depth: maxDepth }),
  });
}

export async function triggerSync(force = false) {
  return fetchJSON('/sync', {
    method: 'POST',
    body: JSON.stringify({ force }),
  });
}

export async function getProdLint() {
  return fetchJSON('/lint/prod');
}
