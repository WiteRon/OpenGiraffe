"""
FastAPI entry point.

All business logic is in src/ package, this is just a thin wrapper
to start the server conveniently.
"""

import uvicorn
from src.container import get_fastapi_app
from src.config.settings import get_settings

# Get configured FastAPI app
app = get_fastapi_app()
settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        workers=1,
    )
