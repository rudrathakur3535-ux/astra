from .app_api import router as app_router
from .avatar_api import router as avatar_router
from .dashboard_api import router as dashboard_router
from .deployment_api import router as deployment_router
from .integrations_api import router as integrations_router
from .learning_api import router as learning_router
from .performance_api import router as performance_router
from .release_api import router as release_router
from .sync_mcp_api import router as sync_mcp_router

__all__ = [
    "app_router",
    "avatar_router",
    "dashboard_router",
    "deployment_router",
    "integrations_router",
    "learning_router",
    "performance_router",
    "release_router",
    "sync_mcp_router"
]
