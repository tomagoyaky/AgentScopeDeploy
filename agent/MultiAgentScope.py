# -*- coding: utf-8 -*-
"""The example of how to construct multi-agent conversation with MsgHub and
pipeline in AgentScope."""
import asyncio
import os
import agentscope

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel, DashScopeChatModel, AnthropicChatModel, GeminiChatModel, GeminiChatModel
from agentscope.pipeline import MsgHub, sequential_pipeline

agentscope.init(
    # ...
    studio_url="http://localhost:3000"
)

def create_participant_agent(
    name: str,
    age: int,
    career: str,
    character: str,
) -> ReActAgent:
    """Create a participant agent with a specific name, age, and character."""
    return ReActAgent(
        name=name,
        sys_prompt=(
            f"You're a {age}-year-old {career} named {name} and you're "
            f"a {character} person."
        ),
       # 模型种类参考： https://doc.agentscope.io/zh_CN/tutorial/task_model.html
        model=OpenAIChatModel(
            model_name="deepseek-v1",
            api_key=os.environ["LLM_API_KEY"],
            stream=True,
        ),
        # Use multiagent formatter because the multiple entities will
        # occur in the prompt of the LLM API call
        formatter=DashScopeMultiAgentFormatter(),
    )


async def main() -> None:
    """Run a multi-agent conversation workflow."""

    # Create multiple participant agents with different characteristics
    alice = create_participant_agent("Alice", 30, "teacher", "friendly")
    bob = create_participant_agent("Bob", 14, "student", "rebellious")
    charlie = create_participant_agent("Charlie", 28, "doctor", "thoughtful")

    # Create a conversation where participants introduce themselves within
    # a message hub
    async with MsgHub(
        participants=[alice, bob, charlie],
        # The greeting message will be sent to all participants at the start
        announcement=Msg(
            "system",
            "Now you meet each other with a brief self-introduction.",
            "system",
        ),
    ) as hub:
        # Quick construct a pipeline to run the conversation
        await sequential_pipeline([alice, bob, charlie])
        # Or by the following way:
        # await alice()
        # await bob()
        # await charlie()

        # Delete a participant agent from the hub and fake a broadcast message
        print("##### We fake Bob's departure #####")
        hub.delete(bob)
        await hub.broadcast(
            Msg(
                "bob",
                "I have to start my homework now, see you later!",
                "assistant",
            ),
        )
        await alice()
        await charlie()

        # ...

if __name__ == "__main__":
    asyncio.run(main())