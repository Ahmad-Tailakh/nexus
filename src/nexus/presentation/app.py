
from fastapi import Depends, FastAPI
from nexus.presentation.dependencies.auth import get_current_user
from nexus.presentation.routers import (
    auth,
    deployments,
    environments,
    health,
    projects,
    services,
)

app = FastAPI(
    title="Nexus API",
    version="0.1.0",
)

# Public endpoints
app.include_router(health.router)
app.include_router(auth.router)

# Authenticated endpoints
app.include_router(projects.router, dependencies=[Depends(get_current_user)])
app.include_router(environments.router, dependencies=[Depends(get_current_user)])
app.include_router(services.router, dependencies=[Depends(get_current_user)])
app.include_router(deployments.router, dependencies=[Depends(get_current_user)])
