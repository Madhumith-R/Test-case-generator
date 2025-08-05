#!/usr/bin/env python3
"""
Setup script for Workik AI Test Case Generator
Helps configure GitHub Personal Access Token
"""

import os
import sys

def main():
    print("🚀 Workik AI Test Case Generator Setup")
    print("=" * 50)
    print()
    
    # Check if .env exists
    env_path = ".env"
    env_example_path = ".env.example"
    
    if not os.path.exists(env_example_path):
        print("❌ .env.example not found!")
        return
    
    # Create .env from template if it doesn't exist
    if not os.path.exists(env_path):
        print("📝 Creating .env file from template...")
        with open(env_example_path, 'r') as f:
            content = f.read()
        with open(env_path, 'w') as f:
            f.write(content)
        print("✅ .env file created!")
    else:
        print("✅ .env file already exists!")
    
    print()
    print("🔑 GitHub Personal Access Token Setup")
    print("-" * 40)
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select these scopes:")
    print("   - ✅ repo (Full control of private repositories)")
    print("   - ✅ user:email (Access user email addresses)")
    print("4. Copy the generated token")
    print()
    
    token = input("📋 Paste your GitHub Personal Access Token here: ").strip()
    
    if not token:
        print("❌ No token provided!")
        return
    
    # Update .env file
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('GITHUB_TOKEN='):
            lines[i] = f'GITHUB_TOKEN={token}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'\nGITHUB_TOKEN={token}\n')
    
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✅ Token saved to .env file!")
    print()
    print("🎉 Setup complete! You can now start the server:")
    print("   python server.py")
    print()

if __name__ == "__main__":
    main()
