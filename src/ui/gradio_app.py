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

    # 完整自定义 CSS - 响应式美化，支持移动端和桌面端
    custom_css = """
    /* 容器自适应 - 大屏居中限制宽度，移动端全屏 */
    .gradio-container {
        max-width: 900px !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 1rem !important;
        box-sizing: border-box;
    }

    /* 渐变标题栏 */
    #chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
    }

    #chat-header h1 {
        color: white !important;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* 聊天框容器 */
    .chatbot-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 100, 100, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 100, 100, 0.5);
    }

    /* 头像样式 */
    .message-avatar {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
    }

    /* 底部输入区域 */
    .input-area {
        margin-top: 1rem;
        gap: 0.5rem;
    }

    /* 按钮美化 */
    .primary-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        transition: transform 0.2s !important;
    }
    .primary-btn:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }

    /* 平板适配 */
    @media screen and (max-width: 1024px) {
        .gradio-container {
            max-width: 100% !important;
            padding: 0.8rem !important;
        }
        #chat-header {
            padding: 1rem;
        }
        #chat-header h1 {
            font-size: 1.5rem;
        }
    }

    /* 手机适配 */
    @media screen and (max-width: 768px) {
        .gradio-container {
            padding: 0.5rem !important;
            max-width: 100% !important;
        }
        #chat-header {
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        #chat-header h1 {
            font-size: 1.25rem;
        }
        .message-avatar {
            width: 32px !important;
            height: 32px !important;
        }
        /* 移动端聊天框高度自适应 */
        .chatbot-container > div {
            height: calc(100vh - 220px) !important;
            min-height: 400px;
        }
    }

    /* 深色模式适配 */
    @media (prefers-color-scheme: dark) {
    }
    """

    # 使用 Soft 主题，支持自动深色模式
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
        radius_size=gr.themes.sizes.radius_lg,
        spacing_size=gr.themes.sizes.spacing_md,
    )

    def respond(message: str, chat_history):
        """Process user message and stream AI response."""
        # Convert Gradio chat history to domain Message objects
        domain_messages = [
            Message(role=msg["role"], content=msg["content"])
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

    # 创建 Gradio 界面
    with gr.Blocks(title="AI 聊天助手") as demo:
        # 渐变标题栏
        gr.HTML("""
        <div id="chat-header">
            <h1>🤖 AI 聊天助手</h1>
        </div>
        """)

        # 聊天框 - 配置头像
        chatbot = gr.Chatbot(
            height=600,
            placeholder="<center style='color: #999; padding: 20px;'>开始与 AI 对话吧！</center>",
            avatar_images=(
                "https://api.dicebear.com/7.x/avataaars/svg?seed=user",
                "https://api.dicebear.com/7.x/bottts/svg?seed=assistant",
            ),
            elem_classes=["chatbot-container"],
        )

        # 输入区域
        with gr.Row(elem_classes=["input-area"]):
            msg = gr.Textbox(
                label="",
                placeholder="请输入你的问题...按回车发送",
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

        # 清空按钮
        with gr.Row():
            clear = gr.Button("清空对话", variant="secondary")

        # 绑定事件
        msg.submit(respond, [msg, chatbot], chatbot)
        submit_btn.click(respond, [msg, chatbot], chatbot)
        clear.click(lambda: None, None, chatbot, queue=False)
        msg.submit(lambda: "", outputs=msg)  # 发送后清空输入框
        submit_btn.click(lambda: "", outputs=msg)

    demo.css = custom_css
    return demo
