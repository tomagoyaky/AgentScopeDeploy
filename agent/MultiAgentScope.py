# -*- coding: utf-8 -*-
"""The example of how to construct multi-agent conversation with MsgHub and
pipeline in AgentScope."""
import asyncio
import os
import json
from typing import Callable, Literal, Any

from pydantic import BaseModel, Field

from agentscope.agent import ReActAgent, AgentBase
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.memory import InMemoryMemory
from agentscope.model import OpenAIChatModel, DashScopeChatModel, AnthropicChatModel, GeminiChatModel, GeminiChatModel
from agentscope.formatter import DashScopeChatFormatter
from agentscope.pipeline import MsgHub, sequential_pipeline
from agentscope.tool import ToolResponse, Toolkit, execute_python_code, execute_shell_command, view_text_file, write_text_file

# agentscope.init(
#     # ...
#     studio_url="http://localhost:3000"
# )


MODEL_NAME="qwen-max"
API_KEY=os.environ["DASHSCOPE_API_KEY"]
STREAMING=True

# 使用结构化输出指定路由任务
class RoutingChoice(BaseModel):
    your_choice: Literal[
        "内容生成",
        "编程",
        "工具调用",
        "产品需求分析",
        None,
    ] = Field(
        description="选择正确的任务类型，如果任务太简单或没有合适的任务，则选择 ``None``",
    )
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
    
class RouterAgent(AgentBase):

    def __init__(self) -> None:
        super().__init__()
        self.router = ReActAgent(
            name="Router",
            sys_prompt="你是一个路由智能体。你的目标是将用户查询路由到正确的后续任务，注意你不需要回答用户的问题。直接结构性输出任务类型就可以了",
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=STREAMING,
            ),
            formatter=DashScopeChatFormatter(),
        )
    async def route(self: AgentBase, task_description: str) -> None:
        # 路由查询
        msg_res = await self.router(
            Msg(
                name="router_agent",
                role="assistant",
                content=task_description,
            ),
            structured_model=RoutingChoice,
        )

        # 结构化输出存储在 metadata 字段中
        print("结构化输出：")
        print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))
        return msg_res

class MasterAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__()
        # self.toolkit = Toolkit()
        # self.toolkit.register_tool_function(execute_python_code)
        # self.toolkit.register_tool_function(execute_shell_command)
        # self.toolkit.register_tool_function(view_text_file)
        # self.toolkit.register_tool_function(write_text_file)

        self.agent = ReActAgent(
            name="master_agent",
            sys_prompt=(
                f"你是一个角色管理智能体。你的任务是分配多个智能体来适配用户的目标，这些智能体需要包括：角色名称、角色描述，以及角色的提示词。注意你不需要回答用户的问题。直接结构性输出角色列表就可以了"
            ),
            # 模型种类参考： https://doc.agentscope.io/zh_CN/tutorial/task_model.html
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=STREAMING,
            ),
            memory=InMemoryMemory(),
            formatter=DashScopeChatFormatter(),
            # toolkit=self.toolkit
        )
    
    async def start(self: AgentBase, task_description: str) -> None:
        msg_res = await self.agent(
            Msg(
                name="master_agent",
                role="assistant",
                content=task_description,
            ),
            structured_model=RoleStructure
        )
        print("结构化输出：")
        print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))

        roles = msg_res.metadata.get("roles", [])
        for role in roles:
            role_name = role.get("role_name")
            role_description = role.get("role_description")
            print(f"角色名称: {role_name}")
            print(f"角色描述: {role_description}")

            summary_req = []
            role = RoleAgent(role_name, role_description)
            role_msg_res = await role.play(Msg(
                    name="master_agent",
                    role="assistant",
                    content=task_description
                )
            )
            role_res = {}
            role_res['role_name'] = role_name
            role_res["content"] = role_msg_res
            summary_req.append(role_res)

        print(json.dumps(summary_req, indent=4, ensure_ascii=False))

        return msg_res
    
    # @staticmethod
    # def instance_pre_reply_hook(
    #     self: AgentBase,
    #     kwargs: dict[str, Any],
    # ) -> dict[str, Any]:
    #     """修改消息内容的前置回复钩子。"""
    #     msg = kwargs["msg"]
    #     msg.content += "[instance-pre-reply]"
    #     # 返回修改后的 kwargs
    #     return {
    #         **kwargs,
    #         "msg": msg,
    #     }

    # @staticmethod
    # def cls_pre_reply_hook(
    #     self: AgentBase,
    #     kwargs: dict[str, Any],
    # ) -> dict[str, Any]:
    #     """修改消息内容的前置回复钩子。"""
    #     msg = kwargs["msg"]
    #     msg.content += "[cls-pre-reply]"
    #     # 返回修改后的 kwargs
    #     return {
    #         **kwargs,
    #         "msg": msg,
    #     }

class RoleAgent(AgentBase):
    def __init__(self, name: str, role_description: str) -> None:
        super().__init__()
        # toolkit = Toolkit()
        # toolkit.register_tool_function(execute_python_code)
        self.name = name
        self.role = ReActAgent(
            name=name,
            sys_prompt=role_description,
            model=DashScopeChatModel(
                model_name=MODEL_NAME,
                api_key=API_KEY,
                stream=STREAMING,
            ),
            formatter=DashScopeChatFormatter(),
            # toolkit=toolkit,
        )
    # 创建子智能体的工具函数
    async def play(
            self: AgentBase,
            role_description: str,
        ) -> ToolResponse:
            # 让子智能体完成任务
            msg_res = await self.role(
                Msg(
                    name="role_agent",
                    role="assistant",
                    content=role_description,
                )
            )
            print("结构化输出：")
            print(json.dumps(msg_res.metadata, indent=4, ensure_ascii=False))
            return msg_res

async def main() -> None:
    # # 注册类钩子
    # MasterAgent.register_class_hook(
    #     hook_type="pre_reply",
    #     hook_name="test_pre_reply",
    #     hook=MasterAgent.cls_pre_reply_hook,
    # )

    agent = MasterAgent()
    router = RouterAgent()
    # # 注册实例钩子
    # agent.register_instance_hook(
    #     hook_type="pre_reply",
    #     hook_name="test_pre_reply",
    #     hook=MasterAgent.instance_pre_reply_hook,
    # )
    
    task_description = f"帮我写一个用户管理系统的产品需求文档"
    choice = await router.route(task_description)
    your_choice = choice.metadata.get("your_choice")
    print("your_choice:", your_choice)

    if your_choice == "内容生成":
        print("处理内容生成任务...")
    elif your_choice == "编程":
        print("处理编程任务...")
    elif your_choice == "工具调用":
        print("处理工具调用任务...")
    elif your_choice == "产品需求分析":
        print("处理产品需求分析任务...")
        await agent.start(task_description)
    else:
        print("未识别的任务类型或无需处理。")


#     """Run a multi-agent conversation workflow."""

#     # Create multiple participant agents with different characteristics
#     alice = agent.create_master_agent("Alice", 30, "teacher", "friendly")
#     bob = agent.create_master_agent("Bob", 14, "student", "rebellious")
#     charlie = agent.create_master_agent("Charlie", 28, "doctor", "thoughtful")

#     # Create a conversation where participants introduce themselves within
#     # a message hub
#     async with MsgHub(
#         participants=[alice, bob, charlie],
#         # The greeting message will be sent to all participants at the start
#         announcement=Msg(
#             "system",
#             "Now you meet each other with a brief self-introduction.",
#             "system",
#         ),
#     ) as hub:
#         # Quick construct a pipeline to run the conversation
#         await sequential_pipeline([alice, bob, charlie])
#         # Or by the following way:
#         # await alice()
#         # await bob()
#         # await charlie()

#         # Delete a participant agent from the hub and fake a broadcast message
#         print("##### We fake Bob's departure #####")
#         hub.delete(bob)
#         await hub.broadcast(
#             Msg(
#                 "bob",
#                 "I have to start my homework now, see you later!",
#                 "assistant",
#             ),
#         )
#         await alice()
#         await charlie()

#         # ...

if __name__ == "__main__":
    asyncio.run(main())