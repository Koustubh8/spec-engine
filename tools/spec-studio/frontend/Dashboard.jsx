import { useState, useEffect } from 'react';
import { getStats, triggerSync, getProdLint } from './api';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState(null);
  const [lintReport, setLintReport] = useState(null);

  useEffect(() => {
    getStats().then(s => { setStats(s); setLoading(false); }).catch(() => setLoading(false));
    getProdLint().then(r => setLintReport(r)).catch(() => {});
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    const r = await triggerSync(false);
    setSyncResult(r.summary);
    setSyncing(false);
    // Refresh stats
    const s = await getStats();
    setStats(s);
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!stats) return <div className="loading error">Failed to load stats</div>;

  const kindColors = {
    spec: '#7c3aed', requirement: '#059669', scenario: '#d97706',
    change: '#dc2626', concept: '#2563eb', task: '#0891b2',
    tool: '#7c3aed', person: '#db2777', organization: '#ca8a04',
    reference: '#6b7280', project: '#0d9488',
  };

  const kindLabels = {
    spec: 'Specs', requirement: 'Requirements', scenario: 'Scenarios',
    change: 'Changes', concept: 'Concepts', task: 'Tasks',
    tool: 'Tools', person: 'People', organization: 'Organizations',
    reference: 'References', project: 'Projects',
  };

  return (
    <div className="dashboard">
      <div className="page-header">
        <h2>Dashboard</h2>
        <button className="btn btn-sync" onClick={handleSync} disabled={syncing}>
          {syncing ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>

      {syncResult && (
        <div className="sync-toast">
          Synced: +{syncResult.nodes_created} nodes, +{syncResult.edges_created} edges
          {syncResult.warnings_count > 0 && ` (${syncResult.warnings_count} warnings)`}
        </div>
      )}

      {lintReport && (
        <div className={`prod-lint-card ${lintReport.status}`}>
          <div className="prod-lint-header">
            <div className="prod-lint-score">
              <span className={`score-circle ${lintReport.status}`}>
                {lintReport.score}/{lintReport.max_score}
              </span>
              <span className="score-label">Production Readiness</span>
            </div>
            <div className="prod-lint-summary">
              {lintReport.rules.filter(r => r.passed).length} passing,{' '}
              {lintReport.rules.filter(r => !r.passed && r.severity === 'error').length} errors,{' '}
              {lintReport.rules.filter(r => !r.passed && r.severity === 'warning').length} warnings
            </div>
          </div>
          <div className="prod-lint-rules">
            {lintReport.rules.filter(r => !r.passed).map(rule => (
              <div key={rule.name} className={`lint-rule ${rule.severity}`}>
                <span className="lint-icon">{rule.severity === 'error' ? '❌' : '⚠️'}</span>
                <span className="lint-name">{rule.name}</span>
                <span className="lint-msg">{rule.message || rule.description}</span>
              </div>
            ))}
            {lintReport.rules.filter(r => r.passed).slice(0, 3).map(rule => (
              <div key={rule.name} className="lint-rule passed">
                <span className="lint-icon">✅</span>
                <span className="lint-name">{rule.name}</span>
              </div>
            ))}
            {lintReport.rules.filter(r => r.passed).length > 3 && (
              <div className="lint-rule passed dim">
                +{lintReport.rules.filter(r => r.passed).length - 3} more passing
              </div>
            )}
          </div>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-value">{stats.total_nodes}</div>
          <div className="stat-label">Total Nodes</div>
        </div>
        <div className="stat-card total">
          <div className="stat-value">{stats.total_edges}</div>
          <div className="stat-label">Total Edges</div>
        </div>
        {stats.last_sync && (
          <div className="stat-card sync-status">
            <div className={`stat-value ${stats.last_sync.status}`}>
              {stats.last_sync.status === 'completed' ? 'OK' : 'FAILED'}
            </div>
            <div className="stat-label">
              Last sync {stats.last_sync.completed_at ? (
                <span title={stats.last_sync.completed_at}>synced</span>
              ) : 'never'}
            </div>
          </div>
        )}
      </div>

      <div className="section">
        <h3>Nodes by Kind</h3>
        <div className="kind-grid">
          {Object.entries(stats.by_kind || {}).map(([kind, count]) => (
            <Link to={`/nodes?kind=${kind}`} key={kind} className="kind-card" style={{ borderLeftColor: kindColors[kind] || '#555' }}>
              <div className="kind-count">{count}</div>
              <div className="kind-name">{kindLabels[kind] || kind}</div>
            </Link>
          ))}
        </div>
      </div>

      <div className="section">
        <h3>Top Predicates</h3>
        <div className="predicate-list">
          {(stats.top_predicates || []).map(p => (
            <div key={p.predicate} className="predicate-item">
              <span className="predicate-name">{p.predicate}</span>
              <span className="predicate-count">{p.count}</span>
              <div className="predicate-bar" style={{ width: `${Math.min(100, (p.count / stats.top_predicates[0]?.count) * 100)}%` }} />
            </div>
          ))}
        </div>
      </div>

      {stats.by_tag && Object.keys(stats.by_tag).length > 0 && (
        <div className="section">
          <h3>Top Tags</h3>
          <div className="tag-cloud">
            {Object.entries(stats.by_tag).map(([tag, count]) => (
              <Link to={`/nodes?tag=${tag}`} key={tag} className="tag-chip" style={{ fontSize: `${0.8 + count * 0.04}rem` }}>
                {tag} ({count})
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
