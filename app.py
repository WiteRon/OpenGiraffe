"""
Gradio UI entry point.

All business logic is in src/ package, this is just a thin wrapper
to start the UI conveniently.
"""

from src.container import get_gradio_app
from src.config.settings import get_settings
from src.common.logging import configure_logging

# Configure logging on startup
configure_logging()

# Get configured Gradio app
demo = get_gradio_app()
settings = get_settings()

if __name__ == "__main__":
    demo.launch(
        server_name=settings.ui_host,
        server_port=settings.ui_port,
        root_path="/points/chatbox",
    )
