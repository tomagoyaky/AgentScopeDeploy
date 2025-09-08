import asyncio
import os
import json
from typing import Callable, Literal, Any

from pydantic import BaseModel, Field
from config import API_KEY, MODEL_NAME, STREAMING

from agentscope.agent import ReActAgent, AgentBase
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter
from agentscope.tool import Toolkit, ToolResponse


# 使用结构化输出指定路由任务
class RoutingChoice(BaseModel):
   your_choice: Literal[
        "内容生成",
        "编程",
        "信息检索",
        "产品需求分析",
        None,
    ] = Field(
        description="选择正确的后续任务，如果任务太简单或没有合适的任务，则选择 ``None``",
    )
   
class RouterAgent(AgentBase):

    def __init__(self, agent_name: str) -> None:
        super().__init__()
        self.agent_name = agent_name
        self.router = ReActAgent(
            name=agent_name,
            sys_prompt="你是一个路由智能体,禁止回答用户的问题，请根据用户输入，直接结构性输出任务类型就可以了",
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=False,
            ),
            formatter=DashScopeChatFormatter(),
        )
    async def route(self: AgentBase, task_description: str, dispatch: Callable) -> None:
        # 路由查询
        msg_res = await self.router(
            Msg(
                name=self.agent_name,
                role="user",
                content=task_description,
            ),
            structured_model=RoutingChoice,
        )

        print("Router Agent结构化输出：")
        print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))
        
        your_choice = msg_res.metadata.get("your_choice")
        await dispatch(your_choice, task_description)
