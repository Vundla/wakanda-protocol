#!/usr/bin/env python3
"""
Development server startup script
"""

import uvicorn
from wakanda.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting Wakanda Protocol Development Server")
    print(f"📍 Server will be available at: http://{settings.host}:{settings.port}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")
    print("🔒 Remember to configure your .env file with proper API keys")
    
    uvicorn.run(
        "wakanda.api.main:app",
        host=settings.host,
        port=settings.port,
        debug=True,
        reload=True,
        access_log=True
    )