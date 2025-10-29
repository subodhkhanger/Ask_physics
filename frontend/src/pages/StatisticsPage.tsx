import { useQuery } from '@tanstack/react-query';
import { ApiService } from '../lib/api';

export default function StatisticsPage() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['statistics'],
    queryFn: () => ApiService.getStatistics(),
  });

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-800">Error loading statistics: {(error as Error).message}</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-10 bg-gray-200 rounded w-1/3 animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-3"></div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">No statistics available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Database Statistics</h1>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Papers Card */}
        <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Papers</h2>
            <svg className="w-10 h-10 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-4xl font-bold text-gray-900 mb-2">{stats.papers}</p>
          <p className="text-gray-700">Total papers in database</p>
        </div>

        {/* Temperature Card */}
        <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Temperature</h2>
            <svg className="w-10 h-10 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-4xl font-bold text-gray-900 mb-2">{stats.temperature.count}</p>
          <p className="text-gray-700">Total measurements</p>
        </div>

        {/* Density Card */}
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Density</h2>
            <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
          </div>
          <p className="text-4xl font-bold text-gray-900 mb-2">{stats.density.count}</p>
          <p className="text-gray-700">Total measurements</p>
        </div>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Temperature Details */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Temperature Statistics</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-gray-200">
              <span className="text-gray-600 font-medium">Total Measurements:</span>
              <span className="text-xl font-bold text-gray-900">{stats.temperature.count}</span>
            </div>
            {stats.temperature.avg_kev !== undefined && (
              <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Average Temperature:</span>
                <span className="text-xl font-bold text-orange-600">
                  {stats.temperature.avg_kev.toFixed(2)} keV
                </span>
              </div>
            )}
            {stats.temperature.min_kev !== undefined && (
              <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Minimum Temperature:</span>
                <span className="text-xl font-bold text-gray-900">
                  {stats.temperature.min_kev.toFixed(2)} keV
                </span>
              </div>
            )}
            {stats.temperature.max_kev !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Maximum Temperature:</span>
                <span className="text-xl font-bold text-gray-900">
                  {stats.temperature.max_kev.toFixed(2)} keV
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Density Details */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Density Statistics</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-gray-200">
              <span className="text-gray-600 font-medium">Total Measurements:</span>
              <span className="text-xl font-bold text-gray-900">{stats.density.count}</span>
            </div>
            {stats.density.avg_density !== undefined && (
              <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Average Density:</span>
                <span className="text-lg font-bold text-blue-600">
                  {stats.density.avg_density.toExponential(2)} m⁻³
                </span>
              </div>
            )}
            {stats.density.min_density !== undefined && (
              <div className="flex justify-between items-center pb-3 border-b border-gray-200">
                <span className="text-gray-600 font-medium">Minimum Density:</span>
                <span className="text-lg font-bold text-gray-900">
                  {stats.density.min_density.toExponential(2)} m⁻³
                </span>
              </div>
            )}
            {stats.density.max_density !== undefined && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Maximum Density:</span>
                <span className="text-lg font-bold text-gray-900">
                  {stats.density.max_density.toExponential(2)} m⁻³
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="card bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900 mb-3">About the Data</h2>
        <p className="text-gray-700 leading-relaxed">
          This database contains plasma physics experimental parameters extracted from scientific literature.
          The data is stored in an RDF knowledge graph powered by Apache Jena Fuseki, enabling complex
          queries and relationships between papers, measurements, and parameters.
        </p>
      </div>
    </div>
  );
}
