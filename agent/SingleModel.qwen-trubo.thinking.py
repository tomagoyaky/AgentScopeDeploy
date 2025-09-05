
import asyncio
import json
import os

from agentscope.message import TextBlock, ToolUseBlock, ThinkingBlock, Msg
from agentscope.model import ChatResponse, DashScopeChatModel

async def example_reasoning() -> None:
    """使用推理模型的示例。"""
    model = DashScopeChatModel(
        model_name="qwen-turbo",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        enable_thinking=True,
    )

    res = await model(
        messages=[
            {"role": "user", "content": "我是谁？"},
        ],
    )

    last_chunk = None
    async for chunk in res:
        last_chunk = chunk
    print("最终响应:")
    print(last_chunk)


asyncio.run(example_reasoning())