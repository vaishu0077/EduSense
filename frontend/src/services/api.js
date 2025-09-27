import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    // Get token from Supabase
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Auth endpoints
  auth: {
    login: (credentials) => apiClient.post('/api/auth/login', credentials),
    register: (userData) => apiClient.post('/api/auth/register', userData),
    logout: () => apiClient.post('/api/auth/logout'),
    me: () => apiClient.get('/api/auth/me'),
  },

  // User endpoints
  users: {
    getProfile: (userId) => apiClient.get(`/api/users/${userId}`),
    updateProfile: (userId, data) => apiClient.put(`/api/users/${userId}`, data),
    getStudents: () => apiClient.get('/api/users/students/'),
  },

  // Content endpoints
  content: {
    getTopics: (params) => apiClient.get('/api/content/topics', { params }),
    getTopic: (topicId) => apiClient.get(`/api/content/topics/${topicId}`),
    getTopicChapters: (topicId) => apiClient.get(`/api/content/topics/${topicId}/chapters`),
    createTopic: (data) => apiClient.post('/api/content/topics', data),
    createChapter: (topicId, data) => apiClient.post(`/api/content/topics/${topicId}/chapters`, data),
    uploadContent: (formData) => apiClient.post('/api/content/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    simplifyContent: (data) => apiClient.post('/api/content/simplify', data),
    getContent: (params) => apiClient.get('/api/content/', { params }),
  },

  // Quiz endpoints
  quizzes: {
    getQuizzes: (params) => apiClient.get('/api/quizzes/', { params }),
    getQuiz: (quizId) => apiClient.get(`/api/quizzes/${quizId}`),
    createQuiz: (data) => apiClient.post('/api/quizzes/', data),
    generateQuiz: (data) => apiClient.post('/api/quizzes/generate', data),
    startAttempt: (quizId) => apiClient.post(`/api/quizzes/${quizId}/attempt`),
    submitAttempt: (attemptId, responses) => apiClient.put(`/api/quizzes/attempts/${attemptId}/submit`, { responses }),
    getAttempt: (attemptId) => apiClient.get(`/api/quizzes/attempts/${attemptId}`),
    getUserAttempts: (userId) => apiClient.get(`/api/quizzes/user/${userId}/attempts`),
  },

  // Analytics endpoints
  analytics: {
    getDashboard: () => apiClient.get('/api/analytics/dashboard'),
    getUserPerformance: (userId) => apiClient.get(`/api/analytics/performance/${userId}`),
    getClassAnalytics: () => apiClient.get('/api/analytics/class-analytics'),
    analyzeWeaknesses: (userId) => apiClient.post('/api/analytics/analyze-weaknesses', { user_id: userId }),
  },

  // AI service endpoints
  ai: {
    generateQuiz: (data) => apiClient.post('/api/ai/generate-quiz', data),
    simplifyText: (data) => apiClient.post('/api/ai/simplify-text', data),
    analyzePerformance: (data) => apiClient.post('/api/ai/analyze-performance', data),
    generateLearningPath: (data) => apiClient.post('/api/ai/generate-learning-path', data),
    predictPerformance: (data) => apiClient.post('/api/ai/predict-performance', data),
    healthCheck: () => apiClient.get('/api/ai/health'),
  },
};

// Utility functions
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
    return { message, status: error.response.status };
  } else if (error.request) {
    // Request was made but no response received
    return { message: 'Network error. Please check your connection.', status: 0 };
  } else {
    // Something else happened
    return { message: error.message || 'An unexpected error occurred', status: 0 };
  }
};

// File upload helper
export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  return apiClient.post('/api/content/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });
};

// Text-to-Speech functionality
export const textToSpeech = (text, options = {}) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 1;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;
    utterance.lang = options.lang || 'en-US';
    
    if (options.voice) {
      utterance.voice = options.voice;
    }
    
    speechSynthesis.speak(utterance);
    return utterance;
  } else {
    console.warn('Speech synthesis not supported');
    return null;
  }
};

// Speech-to-Text functionality
export const speechToText = (options = {}) => {
  return new Promise((resolve, reject) => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = options.continuous || false;
      recognition.interimResults = options.interimResults || false;
      recognition.lang = options.lang || 'en-US';
      
      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0])
          .map(result => result.transcript)
          .join('');
        resolve(transcript);
      };
      
      recognition.onerror = (event) => {
        reject(new Error(`Speech recognition error: ${event.error}`));
      };
      
      recognition.start();
    } else {
      reject(new Error('Speech recognition not supported'));
    }
  });
};

// Get available voices for TTS
export const getAvailableVoices = () => {
  if ('speechSynthesis' in window) {
    return speechSynthesis.getVoices();
  }
  return [];
};

export default api;
