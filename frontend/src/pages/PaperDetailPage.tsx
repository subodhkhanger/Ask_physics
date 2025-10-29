import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ApiService } from '../lib/api';

export default function PaperDetailPage() {
  const { arxivId } = useParams<{ arxivId: string }>();

  const { data: paper, isLoading, error } = useQuery({
    queryKey: ['paper', arxivId],
    queryFn: () => ApiService.getPaper(arxivId!),
    enabled: !!arxivId,
  });

  if (error) {
    return (
      <div className="space-y-4">
        <Link to="/papers" className="text-primary-600 hover:text-primary-700 inline-flex items-center">
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Papers
        </Link>
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-800">Error loading paper: {(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 bg-gray-200 rounded w-24 animate-pulse"></div>
        <div className="card animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="space-y-4">
        <Link to="/papers" className="text-primary-600 hover:text-primary-700 inline-flex items-center">
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Papers
        </Link>
        <div className="card text-center py-12">
          <p className="text-gray-500">Paper not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link to="/papers" className="text-primary-600 hover:text-primary-700 inline-flex items-center">
        <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Papers
      </Link>

      <div className="card">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{paper.title}</h1>

        <div className="space-y-3">
          {paper.authors && (
            <div>
              <span className="font-semibold text-gray-700">Authors:</span>
              <p className="text-gray-900 mt-1">{paper.authors}</p>
            </div>
          )}

          {paper.publication_date && (
            <div>
              <span className="font-semibold text-gray-700">Publication Date:</span>
              <p className="text-gray-900 mt-1">
                {new Date(paper.publication_date).toLocaleDateString()}
              </p>
            </div>
          )}

          <div>
            <span className="font-semibold text-gray-700">arXiv ID:</span>
            <p className="text-gray-900 mt-1">{paper.arxiv_id}</p>
          </div>

          {paper.pdf_url && (
            <div>
              <a
                href={paper.pdf_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF
              </a>
            </div>
          )}
        </div>

        {paper.abstract && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">Abstract</h2>
            <p className="text-gray-700 leading-relaxed">{paper.abstract}</p>
          </div>
        )}
      </div>
    </div>
  );
}
