#!/usr/bin/env python3
"""
Setup script for Gemini API integration
"""
import os
from pathlib import Path

def setup_gemini_env():
    """Setup Gemini API key in .env file"""
    env_file = Path(__file__).parent / ".env"
    env_example_file = Path(__file__).parent / ".env.example"
    
    print("🚀 Workik AI Test Case Generator - Gemini Setup")
    print("=" * 50)
    
    # Check if .env file exists
    if not env_file.exists():
        if env_example_file.exists():
            # Copy from .env.example
            with open(env_example_file, 'r') as src:
                content = src.read()
            with open(env_file, 'w') as dst:
                dst.write(content)
            print("✅ Created .env file from .env.example")
        else:
            print("❌ .env.example file not found!")
            return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Check if GEMINI_API_KEY is already set
    gemini_key_set = False
    for i, line in enumerate(lines):
        if line.startswith('GEMINI_API_KEY=') and not line.startswith('GEMINI_API_KEY=your_gemini_api_key_here'):
            gemini_key_set = True
            break
    
    if gemini_key_set:
        print("✅ Gemini API key is already configured!")
        return True
    
    # Prompt for API key
    print("\n📝 Please enter your Gemini API key:")
    print("   You can get it from: https://aistudio.google.com/app/apikey")
    api_key = input("Gemini API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return False
    
    # Update .env file
    updated_lines = []
    gemini_updated = False
    
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            updated_lines.append(f'GEMINI_API_KEY={api_key}\n')
            gemini_updated = True
        else:
            updated_lines.append(line)
    
    # If GEMINI_API_KEY line wasn't found, add it
    if not gemini_updated:
        updated_lines.append(f'\n# Gemini AI API Key\nGEMINI_API_KEY={api_key}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Gemini API key configured successfully!")
    print("\n🔧 Next steps:")
    print("1. Make sure your GitHub token is also set in .env")
    print("2. Start the backend server: python main.py")
    print("3. Start the frontend server in another terminal")
    
    return True

if __name__ == "__main__":
    setup_gemini_env()
