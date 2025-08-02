#!/usr/bin/env python3
"""
Startup script for Global Medical Guidelines AI Hub
Handles both backend and frontend initialization
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import flask
        import requests
        import beautifulsoup4
        import selenium
        import openai
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js is installed
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} OK")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False
    
    # Check if npm is installed
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()} OK")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not installed")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("⚠️  .env file not found")
        print("Creating from env.example...")
        try:
            with open('env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file from template")
        except FileNotFoundError:
            print("❌ env.example not found")
            return False
    
    # Check OpenAI API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured")
        print("AI features will use fallback mode")
    else:
        print("✅ OpenAI API key configured")
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies if needed"""
    print("📦 Installing frontend dependencies...")
    
    if not Path('node_modules').exists():
        print("Installing npm packages...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return False
        print("✅ Frontend dependencies installed")
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting backend server...")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    try:
        # Import and run Flask app
        from app import app
        print("✅ Backend server started at http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the React frontend development server"""
    print("🌐 Starting frontend server...")
    
    try:
        result = subprocess.run(['npm', 'start'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Frontend start failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🏥 Global Medical Guidelines AI Hub")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("❌ Frontend dependency installation failed")
        sys.exit(1)
    
    print("\n🎯 Starting services...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    print("✅ Backend ready, starting frontend...")
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1) 