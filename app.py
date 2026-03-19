import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv()

# 配置信息 - 从环境变量读取
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3")
MODEL = os.getenv("MODEL", "minimax-m2.5")

# 检查 API_KEY 是否设置
if not API_KEY:
    raise ValueError("请在 .env 文件中设置 API_KEY，例如: API_KEY=your-api-key")

# 初始化 OpenAI 客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def respond(message, chat_history):
    """处理用户消息，流式返回 AI 响应
    """
    # 构建对话历史，Gradio 新版本使用字典格式
    messages = []
    # chat_history 已符合字典格式: [{"role": "user", "content": ...}, ...]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": message})

    # 调用流式 API
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        temperature=0.7,
        max_tokens=2000,
    )

    # 逐块返回响应
    partial_message = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            partial_message += chunk.choices[0].delta.content
            # 输出也是字典格式
            yield chat_history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": partial_message}
            ]


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

if __name__ == "__main__":
    # 绑定 0.0.0.0 监听所有接口，公网通过 IP 访问
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=custom_css,
        theme=theme,
    )
