# -*- coding: utf-8 -*-
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


class RoleItem(BaseModel):
    role_name: str = Field(
        description="角色名称",
    )
    role_description: str = Field(
        description="角色描述",
    )
class RoleStructure(BaseModel):
    roles: list[RoleItem] = Field(
        description="任务列表，每个任务为一个 RoleItem，包含 role_name, role_description 字段",
    )

class RoleAgent(AgentBase):
    def __init__(self, agent_name: str, role_description: str) -> None:
        super().__init__()
        self.agent_name = agent_name
        self.role = ReActAgent(
            name=self.agent_name,
            sys_prompt=role_description,
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=STREAMING,
            ),
            formatter=DashScopeChatFormatter(),
        )
    # 创建子智能体的工具函数
    async def play(
            self: AgentBase,
            role_description: str,
        ) -> str:
            # 让子智能体完成任务
            msg_res = await self.role(
                Msg(
                    name=self.agent_name,
                    role="user",
                    content=role_description,
                )
            )
            print("原始输出：" + msg_res)
            print("结构化输出：")
            print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))
            return msg_res.content