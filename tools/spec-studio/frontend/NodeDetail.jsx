import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getNode } from './api';
import ReactMarkdown from 'react-markdown';

const kindColors = {
  spec: '#7c3aed', requirement: '#059669', scenario: '#d97706',
  change: '#dc2626', concept: '#2563eb', task: '#0891b2',
  tool: '#7c3aed', person: '#db2777', organization: '#ca8a04',
  reference: '#6b7280', project: '#0d9488',
};

export default function NodeDetail() {
  const { slug } = useParams();
  const [node, setNode] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getNode(slug).then(n => { setNode(n); setLoading(false); }).catch(() => setLoading(false));
  }, [slug]);

  if (loading) return <div className="loading">Loading node...</div>;
  if (!node) return <div className="loading error">Node '{slug}' not found</div>;

  const EdgeSection = ({ edges, label, direction }) => {
    if (!edges || edges.length === 0) return null;
    return (
      <div className="edge-section">
        <h4>{label} ({edges.length})</h4>
        <div className="edge-list">
          {edges.map(e => {
            // We need to resolve the linked node
            const linkedId = direction === 'out' ? e.to_node_id : e.from_node_id;
            return (
              <div key={e.id} className="edge-item">
                {direction === 'in' && (
                  <span className="edge-direction">&larr;</span>
                )}
                <span className="edge-predicate">{e.predicate}</span>
                <span className="edge-arrow">{direction === 'out' ? '→' : '←'}</span>
                <Link to={`/nodes/${direction === 'out' ? e.to_slug || '' : e.from_slug || ''}`} className="edge-target">
                  {direction === 'out' ? (e.to_title || `node #${e.to_node_id}`) : (e.from_title || `node #${e.from_node_id}`)}
                </Link>
                {direction === 'out' && (
                  <span className="edge-direction">&rarr;</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const DetailField = ({ label, value }) => {
    if (!value) return null;
    return (
      <div className="detail-field">
        <span className="detail-label">{label}</span>
        <span className="detail-value">{value}</span>
      </div>
    );
  };

  return (
    <div className="node-detail">
      <Link to="/nodes" className="back-link">&larr; Back to nodes</Link>

      <div className="detail-header">
        <span className="kind-badge" style={{ backgroundColor: kindColors[node.kind] || '#555' }}>
          {node.kind}
        </span>
        <h2>{node.title}</h2>
      </div>

      <div className="detail-meta">
        <DetailField label="Slug" value={node.slug} />
        <DetailField label="Strength" value={node.strength} />
        <DetailField label="Status" value={node.status} />
        {node.source_file && <DetailField label="Source" value={node.source_file} />}
        <DetailField label="Created" value={node.created_at && new Date(node.created_at).toLocaleString()} />
        <DetailField label="Updated" value={node.updated_at && new Date(node.updated_at).toLocaleString()} />
      </div>

      {node.tags?.length > 0 && (
        <div className="detail-tags">
          {node.tags.map(t => <span key={t} className="node-tag">{t}</span>)}
        </div>
      )}

      {node.body && (
        <div className="detail-body markdown">
          <ReactMarkdown>{node.body}</ReactMarkdown>
        </div>
      )}

      <div className="detail-edges">
        <EdgeSection edges={node.outgoing_edges} label="Outgoing Edges" direction="out" />
        <EdgeSection edges={node.incoming_edges} label="Incoming Edges" direction="in" />
      </div>
    </div>
  );
}
