from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
import json
from dotenv import load_dotenv
import base64
import google.generativeai as genai
import json as json_module

# Load environment variables
load_dotenv()

app = FastAPI(title="Workik AI Test Case Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)  # Don't auto-error if no header

# Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Personal Access Token option
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FRONTEND_URL = "http://localhost:5174"  # Updated to match current frontend port

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

# Pydantic models
class RepoFilesRequest(BaseModel):
    repoUrl: str

class GenerateSummariesRequest(BaseModel):
    repoUrl: str
    filePaths: List[str]
    framework: str = "jest"  # Default to Jest

class GenerateCodeRequest(BaseModel):
    fileContents: str
    summary: str
    framework: str = "jest"  # Default to Jest

def parse_json_response(text: str) -> list:
    """Parse the output of an LLM call to a JSON array."""
    try:
        # Try to parse as JSON directly
        return json_module.loads(text.strip())
    except json_module.JSONDecodeError:
        # If that fails, try to extract JSON from the text
        import re
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            try:
                return json_module.loads(json_match.group())
            except json_module.JSONDecodeError:
                pass
        # If all else fails, return a single-item list
        return [text.strip()]

# Helper functions
async def get_github_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Extract and validate GitHub token from Authorization header or use personal token"""
    if GITHUB_TOKEN:
        # Use personal access token if available
        return GITHUB_TOKEN
    
    # If no personal token, require Authorization header
    if not credentials:
        raise HTTPException(status_code=401, detail="No authentication provided")
    
    return credentials.credentials

async def validate_github_token(token: str) -> dict:
    """Validate GitHub token by fetching user info"""
    try:
        user_data = await fetch_github_api("https://api.github.com/user", token)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid GitHub token: {str(e)}")

async def fetch_github_api(url: str, token: str, params: dict = None):
    """Make authenticated request to GitHub API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub API error: {response.text}"
            )
        return response.json()

# Routes

@app.get("/")
async def root():
    return {"message": "Workik AI Test Case Generator API"}

@app.get("/api/auth/github")
async def github_auth():
    """Redirect to GitHub OAuth consent screen or indicate token auth"""
    if GITHUB_TOKEN:
        # If using personal token, redirect directly to dashboard
        return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?token=personal")
    
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo,user:email"
    return RedirectResponse(url=github_auth_url)

@app.get("/api/auth/github/callback")
async def github_callback(code: str):
    """Handle GitHub OAuth callback and exchange code for access token"""
    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=no_code")
    
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=no_token")
            
            # Redirect to frontend with token
            return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?token={access_token}")
            
    except Exception as e:
        print(f"Error exchanging code for token: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=auth_failed")

@app.get("/api/auth/check")
async def check_auth():
    """Check if personal token is configured"""
    return {
        "has_token": bool(GITHUB_TOKEN),
        "auth_method": "personal_token" if GITHUB_TOKEN else "oauth"
    }

@app.get("/api/user")
async def get_user(token: str = Depends(get_github_token)):
    """Get authenticated user's profile"""
    try:
        # Validate token by fetching user data
        user_data = await validate_github_token(token)
        return user_data
    except HTTPException as e:
        if e.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid token")
        raise e

@app.get("/api/repos")
async def get_repos(token: str = Depends(get_github_token)):
    """Get user's repositories"""
    try:
        repos_data = await fetch_github_api(
            "https://api.github.com/user/repos",
            token,
            params={"sort": "updated", "per_page": 100}
        )
        return repos_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch repositories")

@app.post("/api/repo/files")
async def get_repo_files(request: RepoFilesRequest, token: str = Depends(get_github_token)):
    """Get file tree for a specific repository"""
    try:
        # Extract owner and repo from URL
        repo_path = request.repoUrl.replace("https://github.com/", "")
        owner, repo = repo_path.split("/")
        
        # Fetch repository tree
        tree_data = await fetch_github_api(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD",
            token,
            params={"recursive": 1}
        )
        
        # Filter for relevant files
        relevant_extensions = {'.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.java', '.cpp', '.c', '.cs', '.php'}
        relevant_files = [
            item for item in tree_data.get("tree", [])
            if item.get("type") == "blob" and any(item.get("path", "").endswith(ext) for ext in relevant_extensions)
        ]
        
        return relevant_files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch repository files")

@app.post("/api/repo/frameworks")
async def get_suggested_frameworks(request: RepoFilesRequest, token: str = Depends(get_github_token)):
    """Analyze repository and suggest appropriate testing frameworks"""
    try:
        # Extract owner and repo from URL
        repo_path = request.repoUrl.replace("https://github.com/", "")
        owner, repo = repo_path.split("/")
        
        # Get repository languages
        languages_data = await fetch_github_api(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            token
        )
        
        # Get repository info for additional context
        repo_data = await fetch_github_api(
            f"https://api.github.com/repos/{owner}/{repo}",
            token
        )
        
        # Determine primary language
        primary_language = None
        if languages_data:
            primary_language = max(languages_data.keys(), key=lambda k: languages_data[k])
        
        # Framework suggestions based on language and repository structure
        frameworks = {
            "JavaScript": [
                {"id": "jest", "name": "Jest", "description": "Popular JavaScript testing framework"},
                {"id": "mocha", "name": "Mocha", "description": "Feature-rich JavaScript test framework"},
                {"id": "cypress", "name": "Cypress", "description": "End-to-end testing framework"},
                {"id": "playwright", "name": "Playwright", "description": "Cross-browser automation library"}
            ],
            "TypeScript": [
                {"id": "jest", "name": "Jest", "description": "Popular JavaScript/TypeScript testing framework"},
                {"id": "vitest", "name": "Vitest", "description": "Fast unit test framework for Vite projects"},
                {"id": "cypress", "name": "Cypress", "description": "End-to-end testing framework"},
                {"id": "playwright", "name": "Playwright", "description": "Cross-browser automation library"}
            ],
            "Python": [
                {"id": "pytest", "name": "pytest", "description": "Simple and scalable Python testing framework"},
                {"id": "unittest", "name": "unittest", "description": "Built-in Python testing framework"},
                {"id": "selenium", "name": "Selenium", "description": "Web application testing framework"},
                {"id": "behave", "name": "Behave", "description": "Behavior-driven development framework"}
            ],
            "Java": [
                {"id": "junit", "name": "JUnit", "description": "Standard testing framework for Java"},
                {"id": "testng", "name": "TestNG", "description": "Testing framework inspired by JUnit"},
                {"id": "selenium", "name": "Selenium", "description": "Web application testing framework"},
                {"id": "mockito", "name": "Mockito", "description": "Mocking framework for unit tests"}
            ],
            "C#": [
                {"id": "nunit", "name": "NUnit", "description": "Unit testing framework for .NET"},
                {"id": "xunit", "name": "xUnit", "description": "Free, open-source testing tool for .NET"},
                {"id": "mstest", "name": "MSTest", "description": "Microsoft's unit testing framework"},
                {"id": "selenium", "name": "Selenium", "description": "Web application testing framework"}
            ],
            "Go": [
                {"id": "testing", "name": "Go Testing", "description": "Built-in Go testing package"},
                {"id": "ginkgo", "name": "Ginkgo", "description": "BDD-style testing framework for Go"},
                {"id": "testify", "name": "Testify", "description": "Testing toolkit with common assertions"}
            ],
            "Ruby": [
                {"id": "rspec", "name": "RSpec", "description": "Behavior-driven development framework"},
                {"id": "minitest", "name": "Minitest", "description": "Complete suite of testing facilities"},
                {"id": "cucumber", "name": "Cucumber", "description": "BDD testing framework"}
            ]
        }
        
        # Default frameworks for unknown languages
        default_frameworks = [
            {"id": "generic", "name": "Generic Testing", "description": "Language-agnostic testing approach"},
            {"id": "selenium", "name": "Selenium", "description": "Web application testing framework"}
        ]
        
        suggested_frameworks = frameworks.get(primary_language, default_frameworks)
        
        return {
            "primary_language": primary_language,
            "all_languages": languages_data,
            "suggested_frameworks": suggested_frameworks,
            "repository_info": {
                "name": repo_data.get("name"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language")
            }
        }
        
    except Exception as e:
        print(f"Error getting framework suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze repository")

@app.post("/api/generate/summaries")
async def generate_summaries(request: GenerateSummariesRequest, token: str = Depends(get_github_token)):
    """Generate test case summaries using Google Gemini"""
    try:
        # Extract owner and repo from URL
        repo_path = request.repoUrl.replace("https://github.com/", "")
        owner, repo = repo_path.split("/")
        
        # Fetch file contents
        concatenated_content = ""
        for file_path in request.filePaths:
            try:
                file_data = await fetch_github_api(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}",
                    token
                )
                
                # Decode base64 content
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                concatenated_content += f"// File: {file_path}\n{content}\n\n"
                
            except Exception as file_error:
                print(f"Error fetching file {file_path}: {file_error}")
                continue
        
        if not gemini_model:
            raise HTTPException(status_code=500, detail="Gemini API not configured")
        
        # Framework-specific prompts
        framework_prompts = {
            "jest": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Jest for JavaScript/React. Focus on component props, state changes, user interactions, and edge cases.",
            "vitest": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Vitest for modern JavaScript/TypeScript projects. Focus on unit tests, component testing, and performance testing.",
            "mocha": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Mocha for JavaScript. Focus on behavior-driven development and asynchronous testing patterns.",
            "cypress": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Cypress for end-to-end testing. Focus on user workflows, UI interactions, and integration testing.",
            "playwright": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Playwright for cross-browser testing. Focus on browser automation, API testing, and visual regression testing.",
            "pytest": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is pytest for Python. Focus on fixtures, parametrized tests, and test discovery patterns.",
            "unittest": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is unittest for Python. Focus on test cases, test suites, and assertion methods.",
            "selenium": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Selenium for web automation. Focus on element interactions, page navigation, and cross-browser compatibility.",
            "junit": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is JUnit for Java. Focus on test methods, annotations, and lifecycle management.",
            "testng": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is TestNG for Java. Focus on data-driven testing, parallel execution, and test configuration.",
            "nunit": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is NUnit for .NET. Focus on test fixtures, assertions, and parameterized tests.",
            "xunit": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is xUnit for .NET. Focus on fact-based testing, theory-based testing, and dependency injection.",
            "rspec": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is RSpec for Ruby. Focus on behavior-driven development, describe blocks, and matchers.",
            "testing": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. The target testing framework is Go's built-in testing package. Focus on table-driven tests, benchmarks, and examples.",
            "generic": "You are an expert Test Case Analyst. Your task is to analyze the following code and suggest a list of concise, one-sentence test case summaries. Use generic testing principles applicable to any framework. Focus on functionality, edge cases, and error handling."
        }
        
        base_prompt = framework_prompts.get(request.framework, framework_prompts["generic"])
        
        # Create prompt
        prompt = f"""{base_prompt} Return your response as a valid JSON array of strings. Do not include any other text, explanation, or markdown formatting.

Code to analyze:
---
{concatenated_content}
---"""
        
        # Generate summaries using Gemini
        response = gemini_model.generate_content(prompt)
        summaries_text = response.text
        
        # Parse the response
        summaries = parse_json_response(summaries_text)
        
        # Ensure we return a list
        if not isinstance(summaries, list):
            summaries = [str(summaries)]
        
        return {"summaries": summaries}
        
    except Exception as e:
        print(f"Error generating summaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summaries")

@app.post("/api/generate/code")
async def generate_code(request: GenerateCodeRequest, token: str = Depends(get_github_token)):
    """Generate test code using Google Gemini"""
    try:
        if not gemini_model:
            raise HTTPException(status_code=500, detail="Gemini API not configured")
        
        # Framework-specific code generation prompts
        framework_code_prompts = {
            "jest": f"You are an expert Jest Test Code Generator. Your task is to write a complete and executable Jest test file based on the provided source code and the specific test case objective. Include necessary imports, setup, and teardown. Only output the raw code for the test file.",
            "vitest": f"You are an expert Vitest Test Code Generator. Your task is to write a complete and executable Vitest test file based on the provided source code and the specific test case objective. Include necessary imports and modern ES6+ syntax. Only output the raw code for the test file.",
            "mocha": f"You are an expert Mocha Test Code Generator. Your task is to write a complete and executable Mocha test file based on the provided source code and the specific test case objective. Include describe blocks, before/after hooks, and proper assertions. Only output the raw code for the test file.",
            "cypress": f"You are an expert Cypress Test Code Generator. Your task is to write a complete and executable Cypress test file based on the provided source code and the specific test case objective. Focus on user interactions and page elements. Only output the raw code for the test file.",
            "playwright": f"You are an expert Playwright Test Code Generator. Your task is to write a complete and executable Playwright test file based on the provided source code and the specific test case objective. Include page interactions and cross-browser testing patterns. Only output the raw code for the test file.",
            "pytest": f"You are an expert pytest Test Code Generator. Your task is to write a complete and executable pytest test file based on the provided source code and the specific test case objective. Include fixtures, parametrize decorators, and proper assertions. Only output the raw code for the test file.",
            "unittest": f"You are an expert unittest Test Code Generator. Your task is to write a complete and executable unittest test file based on the provided source code and the specific test case objective. Include TestCase class, setUp/tearDown methods, and assertions. Only output the raw code for the test file.",
            "selenium": f"You are an expert Selenium Test Code Generator. Your task is to write a complete and executable Selenium test script based on the provided source code and the specific test case objective. Include WebDriver setup, element locators, and browser interactions. Only output the raw code for the test file.",
            "junit": f"You are an expert JUnit Test Code Generator. Your task is to write a complete and executable JUnit test class based on the provided source code and the specific test case objective. Include proper annotations, setup methods, and assertions. Only output the raw code for the test file.",
            "testng": f"You are an expert TestNG Test Code Generator. Your task is to write a complete and executable TestNG test class based on the provided source code and the specific test case objective. Include test groups, data providers, and proper annotations. Only output the raw code for the test file.",
            "nunit": f"You are an expert NUnit Test Code Generator. Your task is to write a complete and executable NUnit test class based on the provided source code and the specific test case objective. Include test fixtures, setup/teardown methods, and assertions. Only output the raw code for the test file.",
            "xunit": f"You are an expert xUnit Test Code Generator. Your task is to write a complete and executable xUnit test class based on the provided source code and the specific test case objective. Include fact-based tests, theory-based tests, and proper assertions. Only output the raw code for the test file.",
            "rspec": f"You are an expert RSpec Test Code Generator. Your task is to write a complete and executable RSpec test file based on the provided source code and the specific test case objective. Include describe blocks, context blocks, and proper matchers. Only output the raw code for the test file.",
            "testing": f"You are an expert Go Testing Code Generator. Your task is to write a complete and executable Go test file based on the provided source code and the specific test case objective. Include table-driven tests and proper error handling. Only output the raw code for the test file.",
            "generic": f"You are an expert Test Code Generator. Your task is to write a complete and executable test file based on the provided source code and the specific test case objective. Use generic testing principles and best practices. Only output the raw code for the test file."
        }
        
        base_prompt = framework_code_prompts.get(request.framework, framework_code_prompts["generic"])
        
        # Create prompt
        prompt = f"""{base_prompt} Do not include markdown fences (```), explanations, or any other text.

**Test Case Objective:** {request.summary}

**Source Code:**
---
{request.fileContents}
---"""
        
        # Generate code using Gemini
        response = gemini_model.generate_content(prompt)
        generated_code = response.text
        
        return {"code": generated_code}
        
    except Exception as e:
        print(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate test code")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
