
import asyncio
import json
import os

from agentscope.message import TextBlock, ToolUseBlock, ThinkingBlock, Msg
from agentscope.model import ChatResponse, DashScopeChatModel

async def example_model_call() -> None:
    """使用 DashScopeChatModel 的示例。"""
    model = DashScopeChatModel(
        model_name="deepseek-v1",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        stream=False,
        base_http_api_url="https://api.deepseek.com/v1/chat/completions"
    )

    res = await model(
        messages=[
            {"role": "user", "content": "你好！"},
        ],
    )

    # 您可以直接使用响应内容创建 ``Msg`` 对象
    msg_res = Msg("Friday", res.content, "assistant")

    print("LLM 返回结果:", res)
    print("作为 Msg 的响应:", msg_res)


asyncio.run(example_model_call())