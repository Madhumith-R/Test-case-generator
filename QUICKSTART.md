# 🚀 Quick Start Guide - Personal Access Token

## Prerequisites
1. **Python 3.8+** installed
2. **Node.js 18+** installed  
3. **Google Gemini API Key**
4. **GitHub Personal Access Token**

## Step 1: Setup GitHub Personal Access Token

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Set expiration and select scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `user:email` - Access user email addresses
4. Copy the generated token

## Step 2: Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

## Step 3: Backend Setup

```bash
cd backend

# Create .env file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env and add your credentials:
# GITHUB_TOKEN=your_personal_access_token_here
# GEMINI_API_KEY=your_gemini_api_key_here

# Install dependencies
pip install -r requirements.txt

# Start backend
python main.py
```

## Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

## Step 5: Access Application

1. Open http://localhost:5173
2. Click "Continue with Personal Token"
3. Start generating test cases!

## Troubleshooting

- **Backend errors**: Check if your GitHub token has correct permissions
- **AI errors**: Ensure your Gemini API key is valid and has sufficient quota
- **Frontend errors**: Verify backend is running on http://localhost:8000
