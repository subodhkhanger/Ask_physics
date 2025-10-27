/**
 * API client for Plasma Physics backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Paper {
  arxiv_id: string;
  title: string;
  authors?: string;
  abstract?: string;
  publication_date?: string;
  pdf_url?: string;
}

export interface PaperList {
  total: number;
  count: number;
  offset: number;
  papers: Paper[];
}

export interface TemperatureMeasurement {
  arxiv_id: string;
  title: string;
  value: number;
  unit: string;
  normalized_value: number;
  confidence: string;
  context?: string;
}

export interface DensityMeasurement {
  arxiv_id: string;
  title: string;
  value: number;
  unit: string;
  normalized_value: number;
  confidence: string;
  context?: string;
}

export interface TemperatureStatistics {
  count: number;
  avg_kev?: number;
  max_kev?: number;
  min_kev?: number;
}

export interface DensityStatistics {
  count: number;
  avg_density?: number;
  max_density?: number;
  min_density?: number;
}

export interface Statistics {
  papers: number;
  temperature: TemperatureStatistics;
  density: DensityStatistics;
}

export interface HealthCheck {
  status: string;
  fuseki_connected: boolean;
  version: string;
}

// API functions
export const ApiService = {
  // Health
  async getHealth(): Promise<HealthCheck> {
    const { data } = await api.get<HealthCheck>('/health');
    return data;
  },

  // Papers
  async getPapers(limit = 20, offset = 0): Promise<PaperList> {
    const { data } = await api.get<PaperList>('/papers', {
      params: { limit, offset },
    });
    return data;
  },

  async getPaper(arxivId: string): Promise<Paper> {
    const { data } = await api.get<Paper>(`/papers/${arxivId}`);
    return data;
  },

  async searchPapers(query: string, limit = 20): Promise<Paper[]> {
    const { data } = await api.get<Paper[]>('/papers/search', {
      params: { q: query, limit },
    });
    return data;
  },

  // Temperatures
  async getTemperatures(
    minTemp?: number,
    maxTemp?: number,
    limit = 100
  ): Promise<TemperatureMeasurement[]> {
    const { data } = await api.get<TemperatureMeasurement[]>('/temperatures', {
      params: { min_temp: minTemp, max_temp: maxTemp, limit },
    });
    return data;
  },

  async getTemperatureStatistics(): Promise<TemperatureStatistics> {
    const { data } = await api.get<TemperatureStatistics>('/temperatures/statistics');
    return data;
  },

  // Densities
  async getDensities(
    minDensity?: number,
    maxDensity?: number,
    limit = 100
  ): Promise<DensityMeasurement[]> {
    const { data } = await api.get<DensityMeasurement[]>('/densities', {
      params: { min_density: minDensity, max_density: maxDensity, limit },
    });
    return data;
  },

  async getDensityStatistics(): Promise<DensityStatistics> {
    const { data } = await api.get<DensityStatistics>('/densities/statistics');
    return data;
  },

  // Statistics
  async getStatistics(): Promise<Statistics> {
    const { data } = await api.get<Statistics>('/statistics');
    return data;
  },
};
