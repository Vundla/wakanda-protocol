"""
Application entry point for Wakanda Protocol
Run with: python -m wakanda
"""

import uvicorn
from wakanda.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "wakanda.api.main:app",
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        reload=settings.debug,
        access_log=True
    )