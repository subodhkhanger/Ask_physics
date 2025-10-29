import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ApiService } from '../lib/api';

export default function DensitiesPage() {
  const [minDensity, setMinDensity] = useState<string>('');
  const [maxDensity, setMaxDensity] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['densities', minDensity, maxDensity],
    queryFn: () =>
      ApiService.getDensities(
        minDensity ? parseFloat(minDensity) : undefined,
        maxDensity ? parseFloat(maxDensity) : undefined,
        100
      ),
  });

  const { data: stats } = useQuery({
    queryKey: ['density-statistics'],
    queryFn: () => ApiService.getDensityStatistics(),
  });

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-800">Error loading densities: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Density Measurements</h1>

      {/* Statistics Card */}
      {stats && (
        <div className="card bg-blue-50 border-blue-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Measurements</p>
              <p className="text-2xl font-bold text-gray-900">{stats.count}</p>
            </div>
            {stats.avg_density && (
              <div>
                <p className="text-sm text-gray-600">Average</p>
                <p className="text-xl font-bold text-gray-900">{stats.avg_density.toExponential(2)} m⁻³</p>
              </div>
            )}
            {stats.min_density && (
              <div>
                <p className="text-sm text-gray-600">Minimum</p>
                <p className="text-xl font-bold text-gray-900">{stats.min_density.toExponential(2)} m⁻³</p>
              </div>
            )}
            {stats.max_density && (
              <div>
                <p className="text-sm text-gray-600">Maximum</p>
                <p className="text-xl font-bold text-gray-900">{stats.max_density.toExponential(2)} m⁻³</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Filter Card */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter by Density Range</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="minDensity" className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Density (m⁻³)
            </label>
            <input
              type="number"
              id="minDensity"
              value={minDensity}
              onChange={(e) => setMinDensity(e.target.value)}
              placeholder="e.g., 1e19"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label htmlFor="maxDensity" className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Density (m⁻³)
            </label>
            <input
              type="number"
              id="maxDensity"
              value={maxDensity}
              onChange={(e) => setMaxDensity(e.target.value)}
              placeholder="e.g., 1e20"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
        {(minDensity || maxDensity) && (
          <button
            onClick={() => {
              setMinDensity('');
              setMaxDensity('');
            }}
            className="mt-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-full"></div>
            </div>
          ))}
        </div>
      ) : data && data.length > 0 ? (
        <div className="space-y-4">
          <p className="text-gray-600">{data.length} measurements found</p>
          {data.map((density, index) => (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">{density.title}</h3>
                <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {density.value} {density.unit}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Normalized:</span> {density.normalized_value.toExponential(2)} m⁻³
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Confidence:</span>{' '}
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  density.confidence === 'high' ? 'bg-green-100 text-green-800' :
                  density.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {density.confidence}
                </span>
              </p>
              {density.context && (
                <p className="text-gray-700 mt-2 italic">"{density.context}"</p>
              )}
              <p className="text-sm text-primary-600 mt-2">arXiv: {density.arxiv_id}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">
            {minDensity || maxDensity ? 'No measurements found in this range' : 'No density measurements available'}
          </p>
        </div>
      )}
    </div>
  );
}
