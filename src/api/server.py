"""
FastAPI server implementation.
All endpoints depend on the ChatProvider abstraction, not concrete implementations.
"""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ..config.settings import Settings
from ..domain.chat import ChatProvider
from ..domain.message import ChatRequest, ChatResponse, Message
from ..common.exceptions import AppError


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
        return {
            "status": "ok",
            "message": "AI Chat API is running",
            "model": settings.model,
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
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
            content = await provider.chat_completion(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            return ChatResponse(content=content)
        except AppError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    async def stream_generator(request: ChatRequest):
        """Generate SSE stream for streaming chat completion."""
        try:
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
        except AppError as e:
            error_data = json.dumps({"error": str(e), "done": True})
            yield f"data: {error_data}\n\n"
        except Exception as e:
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

    return app
