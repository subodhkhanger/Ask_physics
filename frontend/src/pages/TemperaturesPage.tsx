import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ApiService } from '../lib/api';

export default function TemperaturesPage() {
  const [minTemp, setMinTemp] = useState<string>('');
  const [maxTemp, setMaxTemp] = useState<string>('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['temperatures', minTemp, maxTemp],
    queryFn: () =>
      ApiService.getTemperatures(
        minTemp ? parseFloat(minTemp) : undefined,
        maxTemp ? parseFloat(maxTemp) : undefined,
        100
      ),
  });

  const { data: stats } = useQuery({
    queryKey: ['temperature-statistics'],
    queryFn: () => ApiService.getTemperatureStatistics(),
  });

  if (error) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-800">Error loading temperatures: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Temperature Measurements</h1>

      {/* Statistics Card */}
      {stats && (
        <div className="card bg-orange-50 border-orange-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Measurements</p>
              <p className="text-2xl font-bold text-gray-900">{stats.count}</p>
            </div>
            {stats.avg_kev && (
              <div>
                <p className="text-sm text-gray-600">Average</p>
                <p className="text-2xl font-bold text-gray-900">{stats.avg_kev.toFixed(2)} keV</p>
              </div>
            )}
            {stats.min_kev && (
              <div>
                <p className="text-sm text-gray-600">Minimum</p>
                <p className="text-2xl font-bold text-gray-900">{stats.min_kev.toFixed(2)} keV</p>
              </div>
            )}
            {stats.max_kev && (
              <div>
                <p className="text-sm text-gray-600">Maximum</p>
                <p className="text-2xl font-bold text-gray-900">{stats.max_kev.toFixed(2)} keV</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Filter Card */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter by Temperature Range</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="minTemp" className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Temperature (keV)
            </label>
            <input
              type="number"
              id="minTemp"
              value={minTemp}
              onChange={(e) => setMinTemp(e.target.value)}
              placeholder="e.g., 1.0"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label htmlFor="maxTemp" className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Temperature (keV)
            </label>
            <input
              type="number"
              id="maxTemp"
              value={maxTemp}
              onChange={(e) => setMaxTemp(e.target.value)}
              placeholder="e.g., 10.0"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
        {(minTemp || maxTemp) && (
          <button
            onClick={() => {
              setMinTemp('');
              setMaxTemp('');
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
          {data.map((temp, index) => (
            <div key={index} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900 flex-1">{temp.title}</h3>
                <span className="ml-4 px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium">
                  {temp.value} {temp.unit}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Normalized:</span> {temp.normalized_value.toFixed(2)} keV
              </p>
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">Confidence:</span>{' '}
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                  temp.confidence === 'high' ? 'bg-green-100 text-green-800' :
                  temp.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {temp.confidence}
                </span>
              </p>
              {temp.context && (
                <p className="text-gray-700 mt-2 italic">"{temp.context}"</p>
              )}
              <p className="text-sm text-primary-600 mt-2">arXiv: {temp.arxiv_id}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500">
            {minTemp || maxTemp ? 'No measurements found in this range' : 'No temperature measurements available'}
          </p>
        </div>
      )}
    </div>
  );
}
