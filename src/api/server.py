"""
FastAPI server implementation.
All endpoints depend on the ChatProvider abstraction, not concrete implementations.
Serves both AI chat API and static trip diary frontend.
"""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from ..config.settings import Settings
from ..domain.chat import ChatProvider
from ..domain.message import ChatRequest, ChatResponse, Message
from ..common.exceptions import AppError
from ..common.logging import get_logger

logger = get_logger("api")

# Get project root directory - absolute path for production
PROJECT_ROOT = Path("/home/ron/local/self/private")
STATIC_DIR = PROJECT_ROOT / "static"
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def create_app(provider: ChatProvider, settings: Settings) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        provider: The chat provider to use (dependency injection)
        settings: Application settings

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="AI Chat API",
        description="Decoupled AI chat API ready for crewai and ragflow extension",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Root endpoint with service info."""
        logger.info("Root endpoint requested")
        return {
            "status": "ok",
            "message": "AI Chat API is running",
            "model": settings.model,
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        logger.debug("Health check requested")
        return {"status": "healthy"}

    @app.post("/v1/chat/completions", response_model=ChatResponse)
    async def chat_completion(request: ChatRequest):
        """
        Non-streaming chat completion.

        Args:
            request: Chat request with messages and generation parameters

        Returns:
            Complete chat response
        """
        try:
            logger.info(f"Received chat completion request, {len(request.messages)} messages")
            content = await provider.chat_completion(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            logger.info("Chat completion completed successfully")
            return ChatResponse(content=content)
        except AppError as e:
            logger.error(f"Application error in chat completion: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Internal error in chat completion: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    async def stream_generator(request: ChatRequest):
        """Generate SSE stream for streaming chat completion."""
        try:
            logger.info(f"Received streaming chat request, {len(request.messages)} messages")
            async for chunk in provider.stream_completion(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                data = json.dumps({
                    "delta": chunk,
                    "done": False,
                })
                yield f"data: {data}\n\n"
                await asyncio.sleep(0)

            # Send done marker
            yield f"data: {json.dumps({'delta': '', 'done': True})}\n\n"
            logger.info("Streaming chat completed successfully")
        except AppError as e:
            logger.error(f"Application error in streaming chat: {str(e)}")
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"
        except Exception as e:
            logger.error(f"Internal error in streaming chat: {str(e)}", exc_info=True)
            error_data = json.dumps({"error": f"Internal error: {str(e)}", "done": True})
            yield f"data: {error_data}\n\n"

    @app.post("/v1/chat/stream")
    async def chat_stream(request: ChatRequest):
        """
        Streaming chat completion with Server-Sent Events (SSE).

        Args:
            request: Chat request with messages and generation parameters

        Returns:
            Streaming response with SSE format
        """
        return StreamingResponse(
            stream_generator(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    # Mount static files for trip diary
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        app.mount("/points/static", StaticFiles(directory=STATIC_DIR), name="static_points")
        logger.info(f"Static files mounted from {STATIC_DIR}")

    # Trip diary frontend routes
    @app.get("/trip", include_in_schema=False)
    async def trip_diary():
        """Serve desktop trip diary page."""
        html_path = FRONTEND_DIR / "trip" / "mini-trip.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Trip page not found")

    @app.get("/mobile", include_in_schema=False)
    async def trip_diary_mobile():
        """Serve 3D mobile trip diary page."""
        html_path = FRONTEND_DIR / "trip" / "mini-trip-mobile.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Mobile trip page not found")

    @app.get("/earth", include_in_schema=False)
    async def trip_diary_earth():
        """Serve 3D Earth trip diary page (alias for /mobile)."""
        html_path = FRONTEND_DIR / "trip" / "mini-trip-mobile.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Earth page not found")

    @app.get("/points/earth", include_in_schema=False)
    async def trip_diary_points_earth():
        """Serve 3D Earth trip diary page at /points/earth for external reverse proxy."""
        html_path = FRONTEND_DIR / "trip" / "mini-trip-mobile.html"
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Earth page not found")

    @app.get("/", include_in_schema=False)
    async def root_frontend():
        """Root endpoint - redirect to trip diary or show API info."""
        return {
            "status": "ok",
            "message": "Server is running",
            "services": {
                "ai_chat_api": "/v1/chat",
                "trip_diary": "/trip",
                "trip_diary_mobile": "/mobile",
                "health_check": "/health"
            }
        }

    logger.info(f"FastAPI app created, model: {settings.model}, CORS origins: {settings.cors_allow_origins}")
    return app
