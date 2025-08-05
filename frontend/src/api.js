import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('github_token');
  // For personal tokens, the backend handles authentication
  // For OAuth tokens, add Authorization header
  if (token && token !== 'personal') {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const api = {
  // Authentication
  getGitHubAuthUrl: () => `${API_BASE_URL}/auth/github`,
  
  // User data
  getUser: () => apiClient.get('/user'),
  
  // Repositories
  getRepos: () => apiClient.get('/repos'),
  getRepoFiles: (repoUrl) => apiClient.post('/repo/files', { repoUrl }),
  getFrameworks: (repoUrl) => apiClient.post('/repo/frameworks', { repoUrl }),
  
  // AI Generation
  generateSummaries: (repoUrl, filePaths, framework = 'jest') => 
    apiClient.post('/generate/summaries', { repoUrl, filePaths, framework }),
  generateCode: (fileContents, summary, framework = 'jest') => 
    apiClient.post('/generate/code', { fileContents, summary, framework }),
};

export default api;
