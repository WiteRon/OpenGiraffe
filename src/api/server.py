"""
FastAPI server implementation.
All endpoints depend on the ChatProvider abstraction, not concrete implementations.
"""

import json
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from ..config.settings import Settings
from ..domain.chat import ChatProvider
from ..domain.entry import EntryCreate, EntryResponse, EntryUpdate, LocationResponse
from ..domain.message import ChatRequest, ChatResponse, Message
from ..repositories.entry_repository import EntryRepository
from ..common.exceptions import AppError
from ..common.logging import get_logger

logger = get_logger("api")
BASE_DIR = Path(__file__).resolve().parents[2]


def create_app(
    provider,
    settings,
    entry_repository,
):
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

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

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

    @app.get("/mobile")
    async def mobile_page():
        """Serve the mobile globe page from the main API service."""

        return FileResponse(str(BASE_DIR / "mini-trip-mobile.html"))

    @app.get("/admin")
    async def admin_page():
        """Serve the lightweight entry admin page."""

        return FileResponse(str(BASE_DIR / "admin.html"))

    @app.get("/locations", response_model=List[LocationResponse])
    async def list_locations():
        """Return aggregated globe marker data."""

        try:
            return entry_repository.list_locations()
        except Exception as e:
            logger.error(f"Failed to list locations: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to list locations: {str(e)}")

    @app.get("/entries", response_model=List[EntryResponse])
    async def list_entries(
        destination=Query(default=None),
        city=Query(default=None),
        country=Query(default=None),
        entry_date=Query(default=None),
    ):
        """Return entries filtered for destination and city panels."""

        try:
            return entry_repository.list_entries(
                destination=destination,
                city=city,
                country=country,
                entry_date=entry_date,
            )
        except Exception as e:
            logger.error(f"Failed to list entries: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to list entries: {str(e)}")

    @app.get("/entries/{entry_id}", response_model=EntryResponse)
    async def get_entry(entry_id: int):
        """Return a single entry by id."""

        try:
            entry = entry_repository.get_entry(entry_id)
            if entry is None:
                raise HTTPException(status_code=404, detail="Entry not found")
            return entry
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get entry {entry_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to get entry: {str(e)}")

    @app.post("/entries", response_model=EntryResponse, status_code=201)
    async def create_entry(request: EntryCreate):
        """Create a new travel entry."""

        try:
            return entry_repository.create_entry(request)
        except Exception as e:
            logger.error(f"Failed to create entry: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")

    @app.put("/entries/{entry_id}", response_model=EntryResponse)
    async def update_entry(entry_id: int, request: EntryUpdate):
        """Update an existing travel entry."""

        try:
            entry = entry_repository.update_entry(entry_id, request)
            if entry is None:
                raise HTTPException(status_code=404, detail="Entry not found")
            return entry
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update entry {entry_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to update entry: {str(e)}")

    @app.delete("/entries/{entry_id}", status_code=204)
    async def delete_entry(entry_id: int):
        """Delete an existing travel entry."""

        try:
            deleted = entry_repository.delete_entry(entry_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="Entry not found")
            return None
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete entry {entry_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to delete entry: {str(e)}")

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
            if provider is None:
                raise HTTPException(status_code=503, detail="Chat provider is not configured")
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
            if provider is None:
                error_data = json.dumps({"error": "Chat provider is not configured", "done": True})
                yield f"data: {error_data}\n\n"
                return
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

    logger.info(f"FastAPI app created, model: {settings.model}, CORS origins: {settings.cors_allow_origins}")
    return app
