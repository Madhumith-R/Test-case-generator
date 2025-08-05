# Workik AI Test Case Generator

A modern web application that leverages AI to automatically generate intelligent test cases for your code. Connect your GitHub repositories, select files, and let Google Gemini AI create comprehensive test cases for your code across multiple testing frameworks.

## ✨ Features

- 🔐 **GitHub OAuth Integration** - Secure authentication with your GitHub account
- 📁 **Repository Explorer** - Browse and select files from your repositories
- 🤖 **AI-Powered Analysis** - Uses Google Gemini AI for intelligent test generation
- 🧪 **Multi-Framework Support** - Generate tests for Jest, Pytest, JUnit, Selenium, and more
- 📝 **Smart Test Generation** - Creates framework-specific test cases with proper assertions
- 🎨 **Modern UI** - Clean, dark-themed interface built with React and Tailwind CSS
- 📋 **Copy to Clipboard** - Easy code copying with syntax highlighting
- 🐍 **Python Backend** - FastAPI with Google Gemini integration

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, React Router
- **Backend**: Python, FastAPI, HTTPX
- **AI Model**: Google Gemini 1.5 Flash
- **Authentication**: GitHub OAuth 2.0 or Personal Access Token
- **Styling**: Tailwind CSS with custom dark theme

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** and **Node.js** (v18 or higher)
2. **Google Gemini API Key** - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **GitHub Personal Access Token** or **GitHub OAuth App** configured

### Step 1: Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key for use in the configuration

### Step 2: Set Up GitHub Authentication

**Option 1: Personal Access Token (Recommended for development)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` and `user:email` scopes
3. Copy the token

**Option 2: GitHub OAuth App**
1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Workik AI Test Generator
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:8000/api/auth/github/callback`
4. Save the **Client ID** and **Client Secret**

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env  # On Windows
# cp .env.example .env  # On macOS/Linux

# Edit .env file with your credentials
# For Personal Access Token (recommended):
# GITHUB_TOKEN=your_github_personal_access_token_here
# GEMINI_API_KEY=your_gemini_api_key_here

# For OAuth (optional):
# GITHUB_CLIENT_ID=your_client_id_here
# GITHUB_CLIENT_SECRET=your_client_secret_here
# GEMINI_API_KEY=your_gemini_api_key_here

# Start the backend server
python main.py
```

The backend server will start on `http://localhost:8000`

### Step 4: Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

## 📖 How It Works

### Application Flow

1. **Authentication**
   - User clicks "Login with GitHub" on the landing page
   - If using Personal Access Token, automatically redirected to dashboard
   - If using OAuth, redirected to GitHub OAuth consent screen

2. **Repository Selection**
   - Dashboard displays user's repositories in a dropdown
   - Select a repository to load its file tree and suggested testing frameworks
   - Only supported file types are shown (js, jsx, ts, tsx, py, java, etc.)

3. **Framework Selection**
   - AI automatically suggests appropriate testing frameworks based on repository language
   - Choose from Jest, Pytest, JUnit, Selenium, Cypress, and more
   - Framework selection customizes the generated test patterns

4. **File Selection**
   - Choose multiple files using checkboxes
   - Selected files will be analyzed together for context

5. **AI Analysis**
   - Click "Generate [Framework] Tests" to send files to Google Gemini
   - AI analyzes the code and suggests framework-specific test case scenarios
   - Each summary represents a potential test case

6. **Code Generation**
   - Select a test case summary from the list
   - Click "Generate Code" to create framework-specific test code
   - View the generated code with syntax highlighting
   - Copy the code to clipboard for use in your project

### API Endpoints

#### Backend Routes (`http://localhost:8000/api/`)

- `GET /auth/github` - Initiate GitHub OAuth flow or redirect for Personal Token
- `GET /auth/github/callback` - Handle OAuth callback
- `GET /auth/check` - Check authentication method
- `GET /user` - Get authenticated user profile
- `GET /repos` - Get user's repositories
- `POST /repo/files` - Get file tree for a repository
- `POST /repo/frameworks` - Get suggested testing frameworks for a repository
- `POST /generate/summaries` - Generate test case summaries using Google Gemini
- `POST /generate/code` - Generate test code using Google Gemini

#### Google Gemini Integration

The Python backend uses Google's Gemini AI for intelligent test generation:

- **Gemini 1.5 Flash**: Fast and efficient AI model for code analysis
- **Framework-Specific Prompts**: Customized prompts for different testing frameworks
- **JSON Response Parsing**: Reliable extraction of test case summaries
- **Async Operations**: Non-blocking AI operations for better performance

## 🎯 AI Prompts Used

### Test Case Summary Generation

The application uses framework-specific prompts to analyze code and suggest test cases. For example, Jest:

```
You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Jest for JavaScript/React. Focus on component props, state changes, user interactions, and edge cases. Return your response as a valid JSON array of strings. Do not include any other text, explanation, or markdown formatting.

Code to analyze:
---
[File contents here]
---
```

### Test Code Generation

For generating actual framework-specific test code (Jest example):

```
You are an expert Jest Test Code Generator. Your task is to write a complete and executable Jest test file based on the provided source code and the specific test case objective. Include necessary imports, setup, and teardown. Only output the raw code for the test file.

**Test Case Objective:** [Selected summary]

**Source Code:**
---
[File contents here]
---
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# For Personal Access Token (recommended)
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key

# For OAuth (optional)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

### Google Gemini Configuration

Ensure you have a valid Gemini API key:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Add it to your `.env` file as `GEMINI_API_KEY`

## 🚨 Troubleshooting

### Common Issues

1. **"Failed to generate summaries"**
   - Ensure your Gemini API key is valid and properly configured
   - Check if you have sufficient API quota
   - Verify the selected files contain valid code

2. **GitHub authentication errors**
   - For Personal Token: Check if token has `repo` and `user:email` scopes
   - For OAuth: Double-check Client ID and Client Secret in `.env`
   - Ensure callback URL matches your GitHub OAuth app settings
   - Clear browser cache and try again

3. **Repository files not loading**
   - Check if the repository is accessible with your GitHub token
   - Ensure the repository contains supported file types
   - Try refreshing the page or selecting a different repository

4. **Frontend build issues with Tailwind**
   - The CSS errors about `@tailwind` directives are normal in development
   - They don't affect functionality and will be resolved during build

### Debug Mode

To enable verbose logging in the Python backend, you can modify the uvicorn configuration:

```python
# In main.py, at the bottom:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev) for the powerful AI model
- [FastAPI](https://fastapi.tiangolo.com) for the modern Python web framework
- [React](https://reactjs.org) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com) for the styling framework
- [Lucide React](https://lucide.dev) for the beautiful icons

---

**Happy Testing! 🧪✨**
#
