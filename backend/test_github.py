import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('GITHUB_TOKEN')
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json'
}

print("Testing GitHub API...")
print(f"Token loaded: {bool(token)}")

# Test user endpoint
user_response = requests.get('https://api.github.com/user', headers=headers)
print(f"User API Status: {user_response.status_code}")

if user_response.status_code == 200:
    user = user_response.json()
    print(f"User: {user['login']}")
    print(f"Public repos: {user['public_repos']}")
else:
    print(f"User API Error: {user_response.text}")

# Test repos endpoint
repos_response = requests.get('https://api.github.com/user/repos', headers=headers, params={'sort': 'updated', 'per_page': 100})
print(f"Repos API Status: {repos_response.status_code}")

if repos_response.status_code == 200:
    repos = repos_response.json()
    print(f"Found {len(repos)} repositories:")
    for repo in repos[:10]:
        print(f"- {repo['name']} ({repo['html_url']})")
else:
    print(f"Repos API Error: {repos_response.text}")
