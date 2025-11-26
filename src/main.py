"""FastAPI application factory with middleware and exception handlers"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from src.routes import accounts
from src.utils.exceptions import (
    DomainError,
    NotFoundError,
    ValidationError
)
from src.utils.logging import logger, log_request, log_error


def create_app() -> FastAPI:
    """Application factory"""
    app = FastAPI(
        title="Banking REST API",
        description="A banking REST API service with account management, deposits, withdrawals, and transfers",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        """Log incoming requests and response times"""
        start_time = time.time()
        log_request(request.method, request.url.path)
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(f"Response: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response
    
    # Exception handlers
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        """Handle domain errors (400 Bad Request)"""
        log_error(exc, f"{request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(exc)}
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        """Handle not found errors (404 Not Found)"""
        log_error(exc, f"{request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": str(exc)}
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle validation errors (422 Unprocessable Entity)"""
        log_error(exc, f"{request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": str(exc)}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions (500 Internal Server Error)"""
        log_error(exc, f"{request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"}
        )
    
    # Include routers
    app.include_router(accounts.router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}
    
    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

