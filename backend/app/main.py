from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.health import router as health_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(health_router, tags=["Health"])  # also available at /health


@app.get("/")
def root():
    return {
        "message": "Welcome to the Climate Data Platform API",
        "docs_url": "/docs",
        "health_check": "/health",
    }
