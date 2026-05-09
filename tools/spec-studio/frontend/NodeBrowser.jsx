import { useState, useEffect } from 'react';
import { listNodes } from './api';
import { Link, useSearchParams } from 'react-router-dom';

const ALL_KINDS = ['spec', 'requirement', 'scenario', 'change', 'concept', 'task', 'tool', 'person', 'organization', 'reference', 'project'];

const kindColors = {
  spec: '#7c3aed', requirement: '#059669', scenario: '#d97706',
  change: '#dc2626', concept: '#2563eb', task: '#0891b2',
  tool: '#7c3aed', person: '#db2777', organization: '#ca8a04',
  reference: '#6b7280', project: '#0d9488',
};

export default function NodeBrowser() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [nodes, setNodes] = useState([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, page_size: 50 });
  const [loading, setLoading] = useState(true);

  const kind = searchParams.get('kind') || '';
  const tag = searchParams.get('tag') || '';
  const search = searchParams.get('search') || '';
  const page = parseInt(searchParams.get('page') || '1', 10);

  useEffect(() => {
    setLoading(true);
    const params = { page, page_size: 50 };
    if (kind) params.kind = kind;
    if (tag) params.tag = tag;
    if (search) params.search = search;

    listNodes(params).then(r => {
      setNodes(r.data || []);
      setMeta(r.meta);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [kind, tag, search, page]);

  const setFilter = (key, value) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== 'page') next.set('page', '1');
    setSearchParams(next);
  };

  const totalPages = Math.ceil(meta.total / meta.page_size);

  const kindBadge = (k) => (
    <span className="kind-badge" style={{ backgroundColor: kindColors[k] || '#555' }}>{k}</span>
  );

  return (
    <div className="node-browser">
      <div className="page-header">
        <h2>Nodes</h2>
        <span className="meta-count">{meta.total} total</span>
      </div>

      <div className="filters">
        <select value={kind} onChange={e => setFilter('kind', e.target.value)} className="filter-select">
          <option value="">All kinds</option>
          {ALL_KINDS.map(k => (
            <option key={k} value={k}>{k}</option>
          ))}
        </select>

        <input
          type="text"
          placeholder="Search title..."
          value={search}
          onChange={e => setFilter('search', e.target.value)}
          className="filter-input"
        />

        {tag && (
          <span className="active-tag">
            tag: {tag}
            <button onClick={() => setFilter('tag', '')} className="tag-remove">&times;</button>
          </span>
        )}
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : nodes.length === 0 ? (
        <div className="empty-state">
          {search || tag || kind ? 'No nodes match your filters.' : 'No nodes found. Run a sync from the Dashboard.'}
        </div>
      ) : (
        <>
          <div className="node-list">
            {nodes.map(node => (
              <Link to={`/nodes/${node.slug}`} key={node.id} className="node-card">
                <div className="node-card-header">
                  {kindBadge(node.kind)}
                  {node.tags?.slice(0, 3).map(t => (
                    <span key={t} className="node-tag" onClick={e => { e.preventDefault(); setFilter('tag', t); }}>{t}</span>
                  ))}
                </div>
                <div className="node-card-title">{node.title}</div>
                {node.body && <div className="node-card-body">{node.body.slice(0, 150)}</div>}
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button disabled={page <= 1} onClick={() => setFilter('page', String(page - 1))} className="btn-page">
                &larr; Prev
              </button>
              <span className="page-info">Page {page} of {totalPages}</span>
              <button disabled={page >= totalPages} onClick={() => setFilter('page', String(page + 1))} className="btn-page">
                Next &rarr;
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
