#!/usr/bin/env python3
"""
Entry point for running the Horse Breed Service FastAPI application.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        access_log=True
    )