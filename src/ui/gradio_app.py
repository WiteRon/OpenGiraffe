"""
Gradio web UI implementation.
Depends only on the ChatProvider abstraction.
"""

import gradio as gr
from ..config.settings import Settings
from ..domain.chat import ChatProvider
from ..domain.message import Message


def create_gradio_app(provider: ChatProvider, settings: Settings) -> gr.Blocks:
    """
    Create and configure Gradio application.

    Args:
        provider: The chat provider to use (dependency injection)
        settings: Application settings

    Returns:
        Configured Gradio Blocks application
    """

    # Modern minimalist custom CSS - clean design with proper spacing
    custom_css = """
    /* Container - centered with max width, full width on mobile */
    .gradio-container {
        max-width: 800px !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 16px !important;
        box-sizing: border-box;
        background: transparent !important;
    }

    /* Minimal header */
    #chat-header {
        text-align: center;
        padding: 16px 0 20px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        margin-bottom: 16px;
    }

    #chat-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }

    #chat-header p {
        margin: 6px 0 0;
        font-size: 13px;
        color: #888;
    }

    /* Chat container - clean border radius */
    .chatbot-container {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(0, 0, 0, 0.08);
        background: var(--background-fill-primary);
    }

    /* Smooth scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(150, 150, 150, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(150, 150, 150, 0.5);
    }

    /* Avatar - clean circle */
    .message-avatar {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
    }

    /* Input area spacing */
    .input-area {
        margin-top: 16px;
        gap: 8px;
        align-items: center;
    }

    /* Send button - minimal gradient with subtle hover */
    .primary-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        height: auto !important;
    }
    .primary-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35) !important;
    }
    .primary-btn:active {
        transform: translateY(0) !important;
    }

    /* Clear button - subtle */
    .secondary-btn {
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease !important;
    }
    .secondary-btn:hover {
        background: rgba(0, 0, 0, 0.03) !important;
    }

    /* Text input - cleaner */
    .input-area textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        transition: border-color 0.2s !important;
        font-size: 15px !important;
    }
    .input-area textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* Desktop */
    @media screen and (min-width: 768px) {
        .gradio-container {
            padding: 24px !important;
        }
        #chat-header {
            padding: 20px 0 24px;
            margin-bottom: 20px;
        }
    }

    /* Mobile optimization */
    @media screen and (max-width: 768px) {
        .gradio-container {
            padding: 12px 8px !important;
            max-width: 100% !important;
        }
        #chat-header {
            padding: 12px 0 16px;
            margin-bottom: 12px;
        }
        #chat-header h1 {
            font-size: 20px;
        }
        .message-avatar {
            width: 32px !important;
            height: 32px !important;
        }
        .chatbot-container > div {
            height: calc(100vh - 180px) !important;
            min-height: 360px;
        }
        .primary-btn {
            padding: 8px 16px !important;
        }
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .message-avatar {
            border-color: rgba(255, 255, 255, 0.15) !important;
        }
        .chatbot-container {
            border-color: rgba(255, 255, 255, 0.1) !important;
        }
        #chat-header {
            border-bottom-color: rgba(255, 255, 255, 0.1);
        }
    }
    """

    # Modern minimalist theme - monochrome with blue accent
    theme = gr.themes.Glass(
        primary_hue="indigo",
        secondary_hue="slate",
        neutral_hue="slate",
        radius_size=gr.themes.sizes.radius_lg,
        spacing_size=gr.themes.sizes.spacing_md,
    )

    def extract_text_from_content(content) -> str:
        """Extract plain text from Gradio content format.

        Newer Gradio versions store content as list of dicts:
        [{'text': 'hello', 'type': 'text'}, ...]
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
            return " ".join(text_parts)
        return str(content)

    def respond(message: str, chat_history):
        """Process user message and stream AI response."""
        # Convert Gradio chat history to domain Message objects
        domain_messages = [
            Message(role=msg["role"], content=extract_text_from_content(msg["content"]))
            for msg in chat_history
        ]
        domain_messages.append(Message(role="user", content=message))

        # Stream response from provider
        partial_message = ""
        for chunk in provider.stream_completion(domain_messages):
            partial_message += chunk
            # Yield for Gradio streaming display
            yield chat_history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": partial_message}
            ]

    # Create Gradio interface - modern minimalist design
    with gr.Blocks(title="AI Chat") as demo:
        # Minimal header with gradient text
        gr.HTML("""
        <div id="chat-header">
            <h1>🤖 AI Chat</h1>
            <p>基于大语言模型的AI聊天助手</p>
        </div>
        """)

        # Chatbot with custom styling
        chatbot = gr.Chatbot(
            height=560,
            placeholder="<center style='color: #999; padding: 40px 20px;'>💬 输入消息开始对话...</center>",
            avatar_images=(
                "https://api.dicebear.com/7.x/avataaars/svg?seed=Me",
                "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=AI",
            ),
            elem_classes=["chatbot-container"],
        )

        # Input area with clean layout
        with gr.Row(elem_classes=["input-area"]):
            msg = gr.Textbox(
                label="",
                placeholder="输入你的问题...按回车发送",
                scale=4,
                lines=1,
                container=False,
            )
            submit_btn = gr.Button(
                "发送",
                variant="primary",
                scale=1,
                elem_classes=["primary-btn"],
            )

        # Clear button row
        with gr.Row():
            clear = gr.Button(
                "清空对话",
                variant="secondary",
                elem_classes=["secondary-btn"],
            )

        # Event bindings
        msg.submit(respond, [msg, chatbot], chatbot)
        submit_btn.click(respond, [msg, chatbot], chatbot)
        clear.click(lambda: None, None, chatbot, queue=False)
        msg.submit(lambda: "", outputs=msg)  # Clear after send
        submit_btn.click(lambda: "", outputs=msg)

    demo.css = custom_css
    return demo
