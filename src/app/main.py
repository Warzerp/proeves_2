# src/app/main.py

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
from typing import Dict
import os

from .routers import auth, user, query, websocket_chat
from .database.database import Base, engine
from .database.db_config import settings

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear tablas en la base de datos
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas exitosamente")
except Exception as e:
    logger.error(f"Error creando tablas: {str(e)}")
    raise

# Crear aplicación con CDN alternativas para Swagger
app = FastAPI(
    title="SmartHealth API",
    description="API REST y WebSocket para sistema de gestión de salud con RAG",
    version="2.0.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    openapi_url="/openapi.json" if settings.app_env == "development" else None,
    # ✅ URLs alternativas para los assets de Swagger
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True
    }
)

# ============================================================
# MIDDLEWARES DE SEGURIDAD
# ============================================================

# 1. CORS - Configuración permisiva para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo, permitir todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Headers de seguridad solo en producción
    if settings.app_env == "production":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    
    return response

# 3. Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"Time: {process_time:.3f}s "
        f"Path: {request.url.path}"
    )
    
    return response

# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Maneja excepciones HTTP de forma segura"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic"""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Error de validación en los datos enviados",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones generales sin exponer detalles internos"""
    logger.error(f"Unhandled Exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # En desarrollo, mostrar más detalles
    if settings.app_env == "development":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            }
        )
    
    # En producción, mensaje genérico
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Error interno del servidor"
            }
        }
    )

# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(query.router)
app.include_router(websocket_chat.router)

# ============================================================
# ENDPOINTS PRINCIPALES
# ============================================================

@app.get("/", tags=["Root"])
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "API SmartHealth funcionando correctamente",
        "version": "2.0.0",
        "environment": settings.app_env,
        "features": {
            "rest_api": True,
            "websocket": True,
            "rag_enabled": True,
            "streaming": True,
            "authentication": True
        },
        "endpoints": {
            "docs": "/docs" if settings.app_env == "development" else None,
            "redoc": "/redoc" if settings.app_env == "development" else None,
            "websocket": "ws://localhost:8000/ws/chat",
            "health": "/health"
        }
    }

# src/app/main.py - Reemplazar el endpoint /health con esta versión corregida

@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    db_status = "disconnected"
    error_details = None
    
    try:
        # Verificar conexión a base de datos
        from .database.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            # Intentar una query simple
            result = db.execute(text("SELECT 1"))
            result.scalar()
            db_status = "connected"
        except Exception as db_error:
            db_status = "disconnected"
            error_details = str(db_error)
            logger.error(f"Database health check failed: {db_error}")
        finally:
            db.close()
            
    except Exception as e:
        db_status = "error"
        error_details = str(e)
        logger.error(f"Database health check error: {e}")
    
    is_healthy = db_status == "connected"
    
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": time.time(),
        "environment": settings.app_env,
        "services": {
            "database": db_status,
            "llm": "ready",
            "vector_search": "ready",
            "websocket": "enabled"
        }
    }
    
    # Agregar detalles de error en desarrollo
    if not is_healthy and settings.app_env == "development" and error_details:
        response["error"] = error_details
    
    return response
# ============================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    logger.info("=" * 60)
    logger.info("SmartHealth API iniciando")
    logger.info(f"Entorno: {settings.app_env}")
    logger.info(f"Modelo LLM: {settings.llm_model}")
    logger.info(f"Base de datos: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger.info("SmartHealth API cerrando")