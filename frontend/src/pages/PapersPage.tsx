import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ApiService } from '../lib/api';

export default function PapersPage() {
  const [limit] = useState(20);
  const [offset] = useState(0);

  const { data, isLoading, error } = useQuery({
    queryKey: ['papers', limit, offset],
    queryFn: () => ApiService.getPapers(limit, offset),
  });

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-800">Error loading papers: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Papers</h1>
        {data && (
          <p className="text-gray-600">
            Showing {data.papers.length} of {data.total} papers
          </p>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
            </div>
          ))}
        </div>
      ) : data && data.papers.length > 0 ? (
        <div className="space-y-4">
          {data.papers.map((paper) => (
            <Link
              key={paper.arxiv_id}
              to={`/papers/${paper.arxiv_id}`}
              className="card hover:shadow-lg transition-shadow block"
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {paper.title}
              </h3>
              {paper.authors && (
                <p className="text-sm text-gray-600 mb-2">
                  <span className="font-medium">Authors:</span> {paper.authors}
                </p>
              )}
              {paper.abstract && (
                <p className="text-gray-700 line-clamp-3">{paper.abstract}</p>
              )}
              {paper.publication_date && (
                <p className="text-sm text-gray-500 mt-2">
                  Published: {new Date(paper.publication_date).toLocaleDateString()}
                </p>
              )}
              <div className="flex items-center mt-3 text-primary-600">
                <span className="text-sm font-medium">View details</span>
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">No papers found</p>
        </div>
      )}
    </div>
  );
}
