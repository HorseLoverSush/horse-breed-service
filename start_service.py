#!/usr/bin/env python3
"""
Simple startup script for the Horse Breed Service.
This script starts the FastAPI application without requiring database connection initially.
"""

if __name__ == "__main__":
    try:
        from app.main import app
        print("✅ FastAPI app loaded successfully!")
        print("🚀 Starting Horse Breed Service...")
        print("📖 API Documentation available at: http://localhost:8000/docs")
        print("🏥 Health check available at: http://localhost:8000/health")
        
        # Try to start with uvicorn
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            access_log=True
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try installing missing dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        print("💡 Make sure all dependencies are installed and database is configured")