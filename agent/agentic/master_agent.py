# -*- coding: utf-8 -*-
import asyncio
import os
import json
from typing import Callable, Literal, Any

from pydantic import BaseModel, Field
from config import API_KEY, MODEL_NAME, STREAMING
from role_agent import RoleAgent, RoleStructure

from agentscope.agent import ReActAgent, AgentBase
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter

class MasterAgent(AgentBase):
    def __init__(self, agent_name: str) -> None:
        super().__init__()
        self.agent_name = agent_name
        self.agent = ReActAgent(
            name=agent_name,
            sys_prompt=(
                f"你是一个角色管理智能体。你的任务是分配多个智能体来适配用户的目标，这些智能体需要包括：角色名称、角色描述，以及角色的提示词。注意你不需要回答用户的问题，不要输出多余的文字，直接结构性输出json结构"
                f"可以是多个角色，请严格按照以下格式输出：{{'roles': [{{'role_name': '角色名称1', 'role_description': '角色描述1'}}, {{'role_name': '角色名称2', 'role_description': '角色描述2'}}]}}"
            ),
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=False,
            ),
            formatter=DashScopeChatFormatter(),
        )

    async def start(self: AgentBase, task_description: str, callback: Callable) -> None:
        msg_res = await self.agent(
            Msg(
                name=self.agent_name,
                role="user",
                content=task_description,
            ),
            structured_model=RoleStructure
        )
        
        print("Master Agent 结构化输出：")
        print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))
        
        roles = msg_res.metadata.get("roles")
        await callback(roles)