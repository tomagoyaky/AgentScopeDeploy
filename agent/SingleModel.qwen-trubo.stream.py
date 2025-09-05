
import asyncio
import json
import os

from agentscope.message import TextBlock, ToolUseBlock, ThinkingBlock, Msg
from agentscope.model import ChatResponse, DashScopeChatModel

async def example_streaming() -> None:
    """使用流式模型的示例。"""
    model = DashScopeChatModel(
        model_name="qwen-turbo",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        stream=True,
    )
    generator = await model(
        messages=[
            {
                "role": "user",
                "content": "从 1 数到 20，只报告数字，不要任何其他信息。",
            },
        ],
    )
    print("响应的类型:", type(generator))

    i = 0
    async for chunk in generator:
        print(f"块 {i}")
        print(f"\t类型: {type(chunk.content)}")
        print(f"\t{chunk}\n")
        i += 1


asyncio.run(example_streaming())