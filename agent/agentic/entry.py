# -*- coding: utf-8 -*-
import asyncio
from router_agent import RouterAgent
from config import API_KEY, MODEL_NAME, STREAMING

from master_agent import MasterAgent
import json
from typing import Callable, Literal, Any

from pydantic import BaseModel, Field
from config import API_KEY, MODEL_NAME, STREAMING
from role_agent import RoleAgent, RoleStructure

from agentscope.agent import ReActAgent, AgentBase
from agentscope.message import Msg
from agentscope.memory import InMemoryMemory
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter

async def multi_role_dispatch(roles: dict):

    for role in roles:
        role_name = role.get("role_name")
        role_description = role.get("role_description")
        print(f"角色名称: {role_name}")
        print(f"角色描述: {role_description}")

        summary_req = []
        role = RoleAgent(role_name, role_description)
        role_msg_res = await role.play(Msg(
                name=role_name,
                role="user",
                content=role_description
            )
        )
        
        # roles = role_msg_res.metadata.get("roles", [])

        print("multi_role_dispatch 结构化输出：{role_msg_res}")
        print(json.dumps(role_msg_res.metadata, indent=4, ensure_ascii=False))

        role_res = {}
        role_res['role_name'] = role_name
        role_res["content"] = role_msg_res
        summary_req.append(role_res)

    print(json.dumps(summary_req, indent=4, ensure_ascii=False))

async def dispatch(your_choice: str, task_description: str):
    if your_choice == "内容生成":
        print("处理内容生成任务...")
    elif your_choice == "编程":
        print("处理编程任务...")
    elif your_choice == "工具调用":
        print("处理工具调用任务...")
    elif your_choice == "产品需求分析":
        print("处理产品需求分析任务...")
        await MasterAgent("master_agent").start(task_description, multi_role_dispatch)
    else:
        print("未识别的任务类型或无需处理。")
async def main() -> None:
    router = RouterAgent("router_agent")

    task_description = f"帮我写一个用户管理系统的产品需求文档"
    print(f"用户请求: {task_description}, 路由中...")
    await router.route(task_description, dispatch)


if __name__ == "__main__":
    asyncio.run(main())