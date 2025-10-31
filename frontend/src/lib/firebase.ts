/**
 * Firebase Analytics configuration
 */

import { initializeApp } from 'firebase/app';
import { getAnalytics, logEvent as firebaseLogEvent, Analytics } from 'firebase/analytics';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
};

let analytics: Analytics | null = null;

// Initialize Firebase only if config is provided
export const initFirebase = () => {
  // Only initialize if we have a project ID (minimum requirement)
  if (firebaseConfig.projectId) {
    try {
      const app = initializeApp(firebaseConfig);
      analytics = getAnalytics(app);
      console.log('Firebase Analytics initialized');
    } catch (error) {
      console.warn('Firebase Analytics not initialized:', error);
    }
  } else {
    console.log('Firebase Analytics disabled (no config found)');
  }
};

// Log custom events
export const logEvent = (eventName: string, eventParams?: Record<string, any>) => {
  if (analytics) {
    firebaseLogEvent(analytics, eventName, eventParams);
  }
};

// Common analytics events for your app
export const analyticsEvents = {
  // Paper events
  viewPaper: (paperId: string) => {
    logEvent('view_paper', { paper_id: paperId });
  },

  searchPapers: (query: string) => {
    logEvent('search_papers', { search_query: query });
  },

  // Natural language query events
  naturalLanguageQuery: (query: string, resultCount: number) => {
    logEvent('natural_language_query', {
      query: query,
      result_count: resultCount,
    });
  },

  // Filter events
  filterTemperature: (minTemp?: number, maxTemp?: number) => {
    logEvent('filter_temperature', {
      min_temp: minTemp,
      max_temp: maxTemp,
    });
  },

  filterDensity: (minDensity?: number, maxDensity?: number) => {
    logEvent('filter_density', {
      min_density: minDensity,
      max_density: maxDensity,
    });
  },

  // Page view events
  viewPage: (pageName: string) => {
    logEvent('page_view', { page_name: pageName });
  },

  // API interaction events
  apiCall: (endpoint: string, success: boolean, duration: number) => {
    logEvent('api_call', {
      endpoint: endpoint,
      success: success,
      duration_ms: duration,
    });
  },
};

export default analytics;
