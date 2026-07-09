import { useState, useEffect } from 'react'

const DISCREPANCY_LABELS = {
  vintage_mismatch: 'Vintage Mismatch',
  unit_mismatch: 'Unit Mismatch',
  project_type_registry_mismatch: 'Registry Mismatch',
  double_count: 'Double Count',
  double_retired: 'Double Retirement',
}

const DISCREPANCY_COLORS = {
  vintage_mismatch: '#7c3aed',
  unit_mismatch: '#c1440e',
  project_type_registry_mismatch: '#0369a1',
  double_count: '#b45309',
  double_retired: '#be185d',
}

export default function App() {
  const [summary, setSummary] = useState(null)
  const [report, setReport] = useState([])
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch('https://esg-carbon-credit-validator-production.up.railway.app/api/summary')
      .then(r => r.json())
      .then(setSummary)
  }, [])

  useEffect(() => {
    fetch('https://esg-carbon-credit-validator-production.up.railway.app/api/report')
      .then(r => r.json())
      .then(setReport)
  }, [])

  const discrepancyTypes = ['all', ...Object.keys(DISCREPANCY_LABELS)]
  const filtered = filter === 'all' ? report : report.filter(r => r.discrepancy_type === filter)

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          font-family: 'Inter', system-ui, sans-serif;
          background: #f8f7f2;
          color: #1a1a1a;
          min-height: 100vh;
        }

        #root {
          max-width: 100%;
          text-align: left;
        }

        .header {
          background: #2d6a4f;
          padding: 20px 40px;
          display: flex;
          align-items: baseline;
          gap: 16px;
          border-bottom: 3px solid #1a1a1a;
        }

        .header-title {
          font-size: 20px;
          font-weight: 600;
          color: #ffffff;
          letter-spacing: -0.3px;
        }

        .header-sub {
          font-size: 13px;
          color: rgba(255,255,255,0.65);
          font-family: 'JetBrains Mono', monospace;
          letter-spacing: 0.5px;
          text-transform: uppercase;
        }

        .summary-bar {
          display: flex;
          gap: 0;
          border-bottom: 2px solid #1a1a1a;
          background: #ffffff;
        }

        .stat {
          padding: 20px 32px;
          border-right: 1px solid #e5e4e0;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .stat-value {
          font-size: 32px;
          font-weight: 600;
          color: #1a1a1a;
          font-family: 'JetBrains Mono', monospace;
          letter-spacing: -1px;
          line-height: 1;
        }

        .stat-value.flagged {
          color: #c1440e;
        }

        .stat-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #6b7280;
          font-weight: 500;
        }

        .clean-count {
          font-size: 13px;
          color: #2d6a4f;
          font-weight: 500;
          padding: 20px 32px;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .clean-count::before {
          content: '✓';
          font-size: 14px;
        }

        .loading {
          padding: 60px 40px;
          color: #6b7280;
          font-family: 'JetBrains Mono', monospace;
          font-size: 13px;
        }

        .filter-bar {
          padding: 16px 40px;
          display: flex;
          gap: 8px;
          align-items: center;
          border-bottom: 1px solid #e5e4e0;
          background: #f8f7f2;
          flex-wrap: wrap;
        }

        .filter-label {
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #6b7280;
          font-weight: 500;
          margin-right: 4px;
        }

        .filter-btn {
          padding: 4px 12px;
          font-size: 12px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          border: 1.5px solid #1a1a1a;
          background: transparent;
          cursor: pointer;
          border-radius: 2px;
          color: #1a1a1a;
          transition: background 0.1s, color 0.1s;
        }

        .filter-btn:hover {
          background: #1a1a1a;
          color: #ffffff;
        }

        .filter-btn.active {
          background: #1a1a1a;
          color: #ffffff;
        }

        .table-wrap {
          padding: 24px 40px 48px;
        }

        .result-count {
          font-size: 12px;
          color: #6b7280;
          font-family: 'JetBrains Mono', monospace;
          margin-bottom: 12px;
        }

        table {
          width: 100%;
          border-collapse: collapse;
          background: #ffffff;
          border: 2px solid #1a1a1a;
          font-size: 13px;
        }

        thead {
          background: #1a1a1a;
          color: #ffffff;
        }

        th {
          padding: 10px 16px;
          text-align: left;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 1.2px;
          font-weight: 600;
        }

        td {
          padding: 12px 16px;
          border-bottom: 1px solid #e5e4e0;
          vertical-align: top;
        }

        tr:last-child td {
          border-bottom: none;
        }

        tr.flagged-row {
          background: #fdf1ec;
          border-left: 3px solid #c1440e;
        }

        tr.flagged-row td:first-child {
          padding-left: 13px;
        }

        .txn-id {
          font-family: 'JetBrains Mono', monospace;
          font-size: 12px;
          color: #374151;
        }

        .badge {
          display: inline-block;
          padding: 2px 8px;
          border-radius: 2px;
          font-size: 11px;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          letter-spacing: 0.3px;
          border: 1.5px solid currentColor;
        }

        .note-text {
          color: #374151;
          line-height: 1.5;
          max-width: 480px;
        }

        .empty {
          padding: 48px;
          text-align: center;
          color: #6b7280;
          font-size: 13px;
          font-family: 'JetBrains Mono', monospace;
        }
      `}</style>

      <div className="header" style = {{ flexDirection: 'column', alignItems: 'flex-start', gap: '8px'}}>
        <div>
          <span className="header-title">Carbon Credit Discrepancy Validator</span>
          <span className="header-sub">ESG Audit Tool · Synthetic Dataset</span>
        </div>
        <p style = {{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', margin: 0}}>
          A data forensics tool for carbon credit accounting to surface fraud and errors in sustainability data that looks clean on the surface. The single job of the page: make discrepancies visually apparent and make tracking them down more efficient.
        </p>
        
      </div>

      {!summary ? (
        <div className="loading">Loading audit data...</div>
      ) : (
        <>
          <div className="summary-bar">
            <div className="stat">
              <span className="stat-value">{summary.total_transactions}</span>
              <span className="stat-label">Transactions Reviewed</span>
            </div>
            <div className="stat">
              <span className="stat-value flagged">{summary.flagged_rows}</span>
              <span className="stat-label">Discrepancies Flagged</span>
            </div>
            <div className="clean-count">
              {summary.total_transactions - summary.flagged_rows} transactions passed all checks
            </div>
          </div>

          <div className="filter-bar">
            <span className="filter-label">Filter</span>
            {discrepancyTypes.map(type => (
              <button
                key={type}
                className={`filter-btn ${filter === type ? 'active' : ''}`}
                onClick={() => setFilter(type)}
              >
                {type === 'all' ? 'All' : (DISCREPANCY_LABELS[type] || type)}
              </button>
            ))}
          </div>

          <div className="table-wrap">
            <div className="result-count">
              {filtered.length} result{filtered.length !== 1 ? 's' : ''}
              {filter !== 'all' ? ` · ${DISCREPANCY_LABELS[filter] || filter}` : ''}
            </div>

            {filtered.length === 0 ? (
              <div className="empty">No discrepancies match this filter.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Transaction ID</th>
                    <th>Discrepancy Type</th>
                    <th>Note</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((row, i) => {
                    const color = DISCREPANCY_COLORS[row.discrepancy_type] || '#c1440e'
                    return (
                      <tr key={`${row.transaction_id}-${i}`} className="flagged-row">
                        <td>
                          <span className="txn-id">{row.transaction_id}</span>
                        </td>
                        <td>
                          <span
                            className="badge"
                            style={{ color, borderColor: color, background: `${color}12` }}
                          >
                            {DISCREPANCY_LABELS[row.discrepancy_type] || row.discrepancy_type}
                          </span>
                        </td>
                        <td>
                          <span className="note-text">{row.note}</span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </>
  )
}