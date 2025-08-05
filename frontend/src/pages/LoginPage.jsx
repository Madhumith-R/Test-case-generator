import { Github, Code2, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';

function LoginPage() {
  const [authMethod, setAuthMethod] = useState('oauth');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    // Check if personal token is configured and validate it
    const checkAuth = async () => {
      try {
        setLoading(true);
        console.log('Attempting to connect to backend...');
        
        // Use fetch directly for testing
        const response = await fetch('http://localhost:8000/api/auth/check');
        console.log('Backend response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Backend data:', data);
        setAuthMethod(data.auth_method);
        
        // If personal token is configured, validate it by trying to fetch user data
        if (data.auth_method === 'personal_token') {
          try {
            const userResponse = await fetch('http://localhost:8000/api/user');
            if (userResponse.ok) {
              localStorage.setItem('github_token', 'personal');
              navigate('/dashboard');
            } else {
              setError('GitHub token is invalid. Please check your configuration.');
            }
          } catch (userError) {
            console.error('User validation error:', userError);
            setError('GitHub token is invalid. Please check your configuration.');
          }
        }
      } catch (error) {
        console.error('Error checking auth method:', error);
        console.error('Error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack
        });
        setError('Failed to connect to backend. Please ensure the server is running.');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, [navigate]);

  const handleLogin = () => {
    window.location.href = api.getGitHubAuthUrl();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
        <div className="flex items-center space-x-3 text-white">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Checking authentication...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
      <div className="max-w-md w-full mx-4">
        <div className="bg-dark-800 rounded-2xl shadow-2xl p-8 border border-dark-600">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
              <Code2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Workik AI Test Generator
            </h1>
            <p className="text-dark-300 text-lg">
              Generate intelligent test cases for your code
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Features */}
          <div className="mb-8 space-y-3">
            <div className="flex items-center text-dark-200">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <span>Connect your GitHub repositories</span>
            </div>
            <div className="flex items-center text-dark-200">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span>AI-powered test case generation</span>
            </div>
            <div className="flex items-center text-dark-200">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
              <span>Google Gemini AI integration</span>
            </div>
          </div>

          {/* Login Button */}
          <button
            onClick={handleLogin}
            className="w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-3 border border-gray-700 hover:border-gray-600"
          >
            <Github className="w-5 h-5" />
            <span>
              {authMethod === 'personal_token' 
                ? 'Continue with Personal Token' 
                : 'Login with GitHub'}
            </span>
          </button>

          <p className="text-dark-400 text-sm text-center mt-6">
            {authMethod === 'personal_token' 
              ? 'Using configured GitHub Personal Access Token'
              : 'Secure OAuth authentication via GitHub'}
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
