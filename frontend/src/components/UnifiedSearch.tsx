/**
 * Unified Search Component
 *
 * Natural language search interface for plasma physics literature
 */

import React, { useState } from 'react';
import { ApiService, QueryResult, ParsedQuery } from '../lib/api';

const EXAMPLE_QUERIES = [
  "Show me recent research on electron density between 10^16 and 10^18 m^-3",
  "Find papers with temperature above 10 keV",
  "Recent tokamak experiments",
  "Papers about high confinement plasmas",
  "Low temperature plasmas with density measurements",
];

export function UnifiedSearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSparql, setShowSparql] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await ApiService.naturalLanguageQuery(query, 20, showSparql);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="unified-search">
      {/* Search Input */}
      <div className="search-container">
        <label htmlFor="query-input" className="search-label">
          Ask a Question About Plasma Physics Literature
        </label>
        <textarea
          id="query-input"
          className="search-input"
          placeholder="e.g., Show me recent research on electron density in low-temperature plasmas between 10^16 and 10^18 m^-3"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={3}
          disabled={loading}
        />
        <div className="search-actions">
          <button
            className="btn btn-primary"
            onClick={handleSearch}
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={showSparql}
              onChange={(e) => setShowSparql(e.target.checked)}
            />
            Show SPARQL Query
          </label>
        </div>
      </div>

      {/* Example Queries */}
      <div className="examples">
        <h3>Example Queries:</h3>
        <div className="example-chips">
          {EXAMPLE_QUERIES.map((example, idx) => (
            <button
              key={idx}
              className="example-chip"
              onClick={() => handleExampleClick(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="results-container">
          {/* Parsed Query Display */}
          <ParsedQueryDisplay parsed={result.parsed_query} />

          {/* Papers List */}
          <div className="papers-section">
            <h2>
              Found {result.total_results} Paper{result.total_results !== 1 ? 's' : ''}
              {result.execution_time_ms && (
                <span className="execution-time">
                  ({result.execution_time_ms}ms)
                </span>
              )}
            </h2>

            {result.papers.length === 0 ? (
              <div className="no-results">
                <p>No papers found matching your query.</p>
                <p>Try adjusting your parameters or using different keywords.</p>
              </div>
            ) : (
              <div className="papers-list">
                {result.papers.map((paper) => (
                  <div key={paper.arxiv_id} className="paper-card">
                    <h3 className="paper-title">{paper.title}</h3>
                    <div className="paper-meta">
                      <span className="arxiv-id">
                        arXiv:{' '}
                        <a
                          href={`https://arxiv.org/abs/${paper.arxiv_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {paper.arxiv_id}
                        </a>
                      </span>
                      {paper.authors && (
                        <span className="authors">{paper.authors}</span>
                      )}
                      {paper.publication_date && (
                        <span className="date">
                          {new Date(paper.publication_date).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* SPARQL Display */}
          {result.generated_sparql && (
            <div className="sparql-section">
              <h3>Generated SPARQL Query</h3>
              <pre className="sparql-code">{result.generated_sparql}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface ParsedQueryDisplayProps {
  parsed: ParsedQuery;
}

function ParsedQueryDisplay({ parsed }: ParsedQueryDisplayProps) {
  return (
    <div className="parsed-query">
      <h3>Query Interpretation</h3>
      <div className="parsed-content">
        <div className="parsed-item">
          <strong>Intent:</strong>{' '}
          <span className="badge">{parsed.intent}</span>
        </div>

        {Object.entries(parsed.parameters).length > 0 && (
          <div className="parsed-item">
            <strong>Parameters:</strong>
            <ul className="parameters-list">
              {Object.entries(parsed.parameters).map(([key, param]) => (
                <li key={key}>
                  <strong>{key}:</strong>{' '}
                  {param.min_value !== undefined && param.min_value !== null && (
                    <span>
                      {param.min_value} {param.unit}
                    </span>
                  )}
                  {param.min_value !== undefined && param.max_value !== undefined && (
                    <span> to </span>
                  )}
                  {param.max_value !== undefined && param.max_value !== null && (
                    <span>
                      {param.max_value} {param.unit}
                    </span>
                  )}
                  {param.min_value === undefined && param.max_value === undefined && (
                    <span>any {param.unit}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {parsed.keywords.length > 0 && (
          <div className="parsed-item">
            <strong>Keywords:</strong>{' '}
            {parsed.keywords.map((kw, idx) => (
              <span key={idx} className="keyword-badge">
                {kw}
              </span>
            ))}
          </div>
        )}

        {parsed.temporal_constraint && (
          <div className="parsed-item">
            <strong>Time:</strong>{' '}
            <span className="badge">{parsed.temporal_constraint}</span>
          </div>
        )}

        <div className="parsed-item">
          <strong>Confidence:</strong>{' '}
          <span className={`confidence confidence-${getConfidenceLevel(parsed.confidence)}`}>
            {(parsed.confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}

function getConfidenceLevel(confidence: number): string {
  if (confidence >= 0.8) return 'high';
  if (confidence >= 0.5) return 'medium';
  return 'low';
}
