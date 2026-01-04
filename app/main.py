from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import health, research, personas, prioritization
import os

app = FastAPI(
    title="ResearchAI",
    description="AI-powered product research assistant for PMs",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(health.router)
app.include_router(research.router)
app.include_router(personas.router)
app.include_router(prioritization.router)


@app.get("/")
def root():
    """Serve the frontend application"""
    return FileResponse('static/index.html')


@app.get("/api")
def api_root():
    return {
        "message": "Welcome to ResearchAI API",
        "version": "0.1.0",
        "docs": "/docs"
    }
