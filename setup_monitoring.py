#!/usr/bin/env python3
"""
Setup script for the Horse Breed Service with monitoring capabilities.

This script sets up the development environment, installs dependencies,
and starts the service with enhanced monitoring and logging.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, check=True, shell=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=check, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def main():
    """Main setup function."""
    print("🐎 Horse Breed Service - Setup & Monitoring")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists() or not Path("requirements.txt").exists():
        print("❌ Error: Please run this script from the horse-breed-service directory")
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = Path("horse-breed-service-env")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please create it first:")
        print("   python -m venv horse-breed-service-env")
        sys.exit(1)
    
    # Determine the activation script path based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_command = str(venv_path / "Scripts" / "pip.exe")
        python_command = str(venv_path / "Scripts" / "python.exe")
    else:  # Unix/Linux/MacOS
        activate_script = venv_path / "bin" / "activate"
        pip_command = str(venv_path / "bin" / "pip")
        python_command = str(venv_path / "bin" / "python")
    
    if not Path(pip_command).exists():
        print(f"❌ Error: Virtual environment seems incomplete. pip not found at {pip_command}")
        sys.exit(1)
    
    print("✅ Virtual environment found")
    
    # Install/upgrade dependencies
    print("\n📦 Installing dependencies...")
    run_command(f"{pip_command} install --upgrade pip")
    run_command(f"{pip_command} install -r requirements.txt")
    
    print("✅ Dependencies installed successfully")
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Created logs directory")
    
    # Check database connection
    print("\n🗄️  Checking database setup...")
    try:
        result = run_command(f"{python_command} -c \"from app.db.database import engine; engine.connect(); print('Database connection successful')\"", check=False)
        if result.returncode == 0:
            print("✅ Database connection successful")
        else:
            print("⚠️  Database connection failed. Make sure PostgreSQL is running and configured.")
            print("   You can continue, but some features may not work.")
    except Exception as e:
        print(f"⚠️  Could not test database connection: {e}")
    
    # Run database setup if needed
    setup_db = input("\n🔧 Do you want to set up the database tables? (y/N): ").lower().strip()
    if setup_db == 'y':
        print("Setting up database tables...")
        run_command(f"{python_command} create_tables.py", check=False)
        
        seed_data = input("📝 Do you want to seed with sample data? (y/N): ").lower().strip()
        if seed_data == 'y':
            run_command(f"{python_command} seed_data.py", check=False)
    
    # Show monitoring endpoints
    print("\n📊 Monitoring Endpoints Available:")
    print("   • Health Check: http://localhost:8000/api/v1/monitoring/health")
    print("   • Detailed Health: http://localhost:8000/api/v1/monitoring/health/detailed")
    print("   • Metrics: http://localhost:8000/api/v1/monitoring/metrics")
    print("   • Performance: http://localhost:8000/api/v1/monitoring/metrics/performance")
    print("   • Logs: http://localhost:8000/api/v1/monitoring/logs/metrics")
    print("   • Status: http://localhost:8000/api/v1/monitoring/status")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Dashboard: Open monitoring_dashboard.html in your browser")
    
    # Option to start the service
    start_service = input("\n🚀 Do you want to start the service now? (Y/n): ").lower().strip()
    if start_service != 'n':
        print("\n🎯 Starting Horse Breed Service with enhanced monitoring...")
        print("   Service will be available at: http://localhost:8000")
        print("   Press Ctrl+C to stop the service")
        print("-" * 50)
        
        # Start the service with hot reload
        try:
            run_command(f"{python_command} -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info")
        except KeyboardInterrupt:
            print("\n👋 Service stopped. Thank you for using Horse Breed Service!")
    else:
        print("\n📝 To start the service manually, run:")
        if os.name == 'nt':  # Windows
            print(f"   {activate_script} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        else:
            print(f"   source {activate_script} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n✨ Setup complete! Happy coding! 🐎")


if __name__ == "__main__":
    main()