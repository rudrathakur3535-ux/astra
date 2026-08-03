"""
API Router and Endpoints for Project Astra OS.
"""

from app.api.dashboard_api import router as dashboard_router
from app.api.app_api import router as app_router
from app.api.avatar_api import router as avatar_router
from app.api.deployment_api import router as deployment_router
from app.api.sync_mcp_api import router as sync_mcp_router
from app.api.integrations_api import router as integrations_router
from app.api.performance_api import router as performance_router
from app.api.learning_api import router as learning_router
from app.api.release_api import router as release_router

__all__ = [
    "dashboard_router",
    "app_router",
    "avatar_router",
    "deployment_router",
    "sync_mcp_router",
    "integrations_router",
    "performance_router",
    "learning_router",
    "release_router"
]
