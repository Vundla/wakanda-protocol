"""
Main FastAPI application for Wakanda Protocol
Orchestrates all modules and provides unified API gateway
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import structlog
from typing import Dict, Any

from ..core.config import settings
from ..core.security import security_manager, TokenData
from .routes import (
    health,
    auth,
    fintech,
    minerals,
    ai,
    governance,
    infrastructure
)

# Setup structured logging
logger = structlog.get_logger()

# Security scheme
security = HTTPBearer()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="African Sovereignty Blueprint - Full-stack platform for financial, technological, and civic empowerment",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add routes
    setup_routes(app)
    
    # Add event handlers
    setup_event_handlers(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    return app


def setup_middleware(app: FastAPI):
    """Setup application middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure properly in production
        )
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        headers = security_manager.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        return response
    
    # Logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response


def setup_routes(app: FastAPI):
    """Setup application routes"""
    
    # Health check
    app.include_router(health.router, prefix="/health", tags=["Health"])
    
    # Authentication
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    
    # Feature modules (enabled by configuration)
    if settings.enable_fintech:
        app.include_router(fintech.router, prefix="/fintech", tags=["Fintech"])
    
    if settings.enable_minerals:
        app.include_router(minerals.router, prefix="/minerals", tags=["Minerals"])
    
    if settings.enable_ai:
        app.include_router(ai.router, prefix="/ai", tags=["AI Services"])
    
    if settings.enable_governance:
        app.include_router(governance.router, prefix="/governance", tags=["Governance"])
    
    if settings.enable_infrastructure:
        app.include_router(infrastructure.router, prefix="/infrastructure", tags=["Infrastructure"])


def setup_event_handlers(app: FastAPI):
    """Setup application event handlers"""
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Wakanda Protocol starting up")
        # Initialize database connections, caches, etc.
        
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Wakanda Protocol shutting down")
        # Clean up resources


# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenData:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    token_data = security_manager.verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


# Dependency for optional authentication
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenData | None:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            url=str(request.url),
            method=request.method
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )


# Import time for middleware
import time

# Create the application instance
app = create_app()