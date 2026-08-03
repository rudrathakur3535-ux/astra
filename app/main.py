"""
FastAPI Server Entrypoint for Project Astra OS v1.0.
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
import os

from app.api import (
    dashboard_router,
    app_router,
    avatar_router,
    deployment_router,
    sync_mcp_router,
    integrations_router,
    performance_router,
    learning_router,
    release_router
)

app = FastAPI(
    title="Project Astra OS v1.0 Release Candidate",
    description="Modular AI Operating System for Developers",
    version="1.0.0-RC"
)

# Enable CORS for desktop Electron and browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API Routers
app.include_router(dashboard_router)
app.include_router(app_router)
app.include_router(avatar_router)
app.include_router(deployment_router)
app.include_router(sync_mcp_router)
app.include_router(integrations_router)
app.include_router(performance_router)
app.include_router(learning_router)
app.include_router(release_router)

# Mount avatar renderer static files directory if present
renderer_dir = os.path.join(os.path.dirname(__file__), "avatar", "renderer")
if os.path.exists(renderer_dir):
    app.mount("/avatar/static", StaticFiles(directory=renderer_dir), name="avatar_static")


@app.get("/", response_class=JSONResponse)
async def root():
    return {
        "app": "Project Astra OS",
        "version": "v1.0.0-RC",
        "status": "RUNNING",
        "dashboard_url": "http://localhost:8000/dashboard",
        "avatar_studio_url": "http://localhost:8000/avatar/view",
        "docs_url": "http://localhost:8000/docs",
        "timestamp": time.time()
    }
