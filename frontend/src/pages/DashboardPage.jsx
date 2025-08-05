import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  LogOut, 
  Folder, 
  FileText, 
  Loader2, 
  Sparkles,
  ChevronDown,
  User
} from 'lucide-react';
import { api } from '../api';
import SummariesList from '../components/SummariesList';
import CodeDisplay from '../components/CodeDisplay';

function DashboardPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // State management
  const [user, setUser] = useState(null);
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [frameworks, setFrameworks] = useState([]);
  const [selectedFramework, setSelectedFramework] = useState('');
  const [summaries, setSummaries] = useState([]);
  const [activeSummary, setActiveSummary] = useState(null);
  const [generatedCode, setGeneratedCode] = useState('');
  
  // Loading states
  const [loading, setLoading] = useState({
    user: true,
    repos: false,
    files: false,
    frameworks: false,
    summaries: false,
    code: false
  });

  // Check for token and fetch initial data
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get('token');
    
    if (token === 'personal') {
      // Using personal token configured in backend
      localStorage.setItem('github_token', 'personal');
      // Clean URL
      navigate('/dashboard', { replace: true });
    } else if (token) {
      // OAuth token
      localStorage.setItem('github_token', token);
      // Clean URL
      navigate('/dashboard', { replace: true });
    }
    
    const savedToken = localStorage.getItem('github_token');
    if (!savedToken) {
      navigate('/');
      return;
    }
    
    fetchUser();
  }, [location, navigate]);

  // Fetch user data
  const fetchUser = async () => {
    try {
      setLoading(prev => ({ ...prev, user: true }));
      const response = await api.getUser();
      setUser(response.data);
      fetchRepos();
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('github_token');
      navigate('/');
    } finally {
      setLoading(prev => ({ ...prev, user: false }));
    }
  };

  // Fetch repositories
  const fetchRepos = async () => {
    try {
      setLoading(prev => ({ ...prev, repos: true }));
      const response = await api.getRepos();
      setRepos(response.data);
    } catch (error) {
      console.error('Error fetching repos:', error);
    } finally {
      setLoading(prev => ({ ...prev, repos: false }));
    }
  };

  // Fetch files for selected repository
  const fetchFiles = async (repoUrl) => {
    try {
      setLoading(prev => ({ ...prev, files: true, frameworks: true }));
      const [filesResponse, frameworksResponse] = await Promise.all([
        api.getRepoFiles(repoUrl),
        api.getFrameworks(repoUrl)
      ]);
      setFiles(filesResponse.data);
      setFrameworks(frameworksResponse.data.frameworks || []);
      setSelectedFramework(frameworksResponse.data.frameworks?.[0]?.name || '');
      setSelectedFiles([]);
      setSummaries([]);
      setActiveSummary(null);
      setGeneratedCode('');
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setLoading(prev => ({ ...prev, files: false, frameworks: false }));
    }
  };

  // Handle repository selection
  const handleRepoSelect = (repo) => {
    setSelectedRepo(repo);
    fetchFiles(repo.html_url);
  };

  // Handle file selection
  const handleFileToggle = (filePath) => {
    setSelectedFiles(prev => 
      prev.includes(filePath)
        ? prev.filter(f => f !== filePath)
        : [...prev, filePath]
    );
  };

  // Generate summaries
  const generateSummaries = async () => {
    if (!selectedRepo || selectedFiles.length === 0) return;
    
    try {
      setLoading(prev => ({ ...prev, summaries: true }));
      const framework = selectedFramework || 'jest'; // Default to Jest if no framework selected
      const response = await api.generateSummaries(selectedRepo.html_url, selectedFiles, framework);
      setSummaries(response.data.summaries || []);
      setActiveSummary(null);
      setGeneratedCode('');
    } catch (error) {
      console.error('Error generating summaries:', error);
      setSummaries(['Error generating summaries. Please try again.']);
    } finally {
      setLoading(prev => ({ ...prev, summaries: false }));
    }
  };

  // Generate code for selected summary
  const generateCode = async () => {
    if (!selectedRepo || !activeSummary) return;
    
    try {
      setLoading(prev => ({ ...prev, code: true }));
      
      // Get file contents for the selected files
      let fileContents = '';
      for (const filePath of selectedFiles) {
        // This is a simplified approach - in a real app, you'd fetch the actual content
        fileContents += `// File: ${filePath}\n// Content would be fetched here\n\n`;
      }
      
      const framework = selectedFramework || 'jest'; // Default to Jest if no framework selected
      const response = await api.generateCode(fileContents, activeSummary, framework);
      setGeneratedCode(response.data.code || '');
    } catch (error) {
      console.error('Error generating code:', error);
      setGeneratedCode('Error generating code. Please try again.');
    } finally {
      setLoading(prev => ({ ...prev, code: false }));
    }
  };

  // Logout
  const handleLogout = () => {
    localStorage.removeItem('github_token');
    navigate('/');
  };

  if (loading.user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-900">
        <div className="flex items-center space-x-3 text-white">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      {/* Header */}
      <header className="bg-dark-800 border-b border-dark-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Sparkles className="w-8 h-8 text-blue-500" />
            <h1 className="text-xl font-bold">Workik AI Test Generator</h1>
          </div>
          
          {user && (
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <img 
                  src={user.avatar_url} 
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm font-medium">{user.name || user.login}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-dark-700 hover:bg-dark-600 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Sidebar */}
        <div className="w-80 bg-dark-800 border-r border-dark-700 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Repository Selection */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">
                Select Repository
              </label>
              <div className="relative">
                <select
                  value={selectedRepo?.id || ''}
                  onChange={(e) => {
                    const repo = repos.find(r => r.id.toString() === e.target.value);
                    if (repo) handleRepoSelect(repo);
                  }}
                  className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm appearance-none cursor-pointer hover:border-dark-500 focus:border-blue-500 focus:outline-none"
                  disabled={loading.repos}
                >
                  <option value="">Choose a repository...</option>
                  {repos.map(repo => (
                    <option key={repo.id} value={repo.id}>
                      {repo.name} {repo.private && '(Private)'}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-2.5 w-4 h-4 text-dark-400 pointer-events-none" />
              </div>
              {loading.repos && (
                <div className="flex items-center space-x-2 mt-2 text-sm text-dark-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Loading repositories...</span>
                </div>
              )}
            </div>

            {/* File Selection */}
            {selectedRepo && (
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Select Files ({selectedFiles.length} selected)
                </label>
                <div className="max-h-64 overflow-y-auto border border-dark-600 rounded-lg">
                  {loading.files ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="w-5 h-5 animate-spin text-dark-400" />
                    </div>
                  ) : files.length === 0 ? (
                    <div className="text-center py-8 text-dark-400 text-sm">
                      No supported files found
                    </div>
                  ) : (
                    <div className="p-2">
                      {files.map(file => (
                        <label
                          key={file.path}
                          className="flex items-center space-x-3 p-2 hover:bg-dark-700 rounded cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFiles.includes(file.path)}
                            onChange={() => handleFileToggle(file.path)}
                            className="rounded border-dark-500 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
                          />
                          <FileText className="w-4 h-4 text-dark-400 flex-shrink-0" />
                          <span className="text-sm text-dark-200 truncate">
                            {file.path}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Framework Selection */}
            {selectedRepo && frameworks.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Test Framework
                </label>
                <div className="relative">
                  <select
                    value={selectedFramework}
                    onChange={(e) => setSelectedFramework(e.target.value)}
                    className="w-full bg-dark-700 border border-dark-600 rounded-lg px-3 py-2 text-sm appearance-none cursor-pointer hover:border-dark-500 focus:border-blue-500 focus:outline-none"
                    disabled={loading.frameworks}
                  >
                    {frameworks.map(framework => (
                      <option key={framework.name} value={framework.name}>
                        {framework.name} - {framework.description}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-2.5 w-4 h-4 text-dark-400 pointer-events-none" />
                </div>
                {loading.frameworks && (
                  <div className="flex items-center space-x-2 mt-2 text-sm text-dark-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Loading frameworks...</span>
                  </div>
                )}
                {selectedFramework && frameworks.find(f => f.name === selectedFramework) && (
                  <div className="mt-2 p-3 bg-dark-700 rounded-lg">
                    <p className="text-xs text-dark-300">
                      {frameworks.find(f => f.name === selectedFramework)?.description}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Generate Summaries Button */}
            {selectedFiles.length > 0 && (
              <button
                onClick={generateSummaries}
                disabled={loading.summaries}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                {loading.summaries ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Generate {selectedFramework || 'Jest'} Tests</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          {summaries.length === 0 && !generatedCode ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-dark-400">
                <Folder className="w-16 h-16 mx-auto mb-4 text-dark-600" />
                <p className="text-lg">Select files and generate summaries to begin</p>
              </div>
            </div>
          ) : (
            <div className="p-6">
              {summaries.length > 0 && !generatedCode && (
                <SummariesList
                  summaries={summaries}
                  activeSummary={activeSummary}
                  onSummarySelect={setActiveSummary}
                  onGenerateCode={generateCode}
                  loading={loading.code}
                />
              )}
              
              {generatedCode && (
                <CodeDisplay
                  code={generatedCode}
                  onBack={() => setGeneratedCode('')}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
