"""AlertAgent - a specialized assistant for alert management."""

import asyncio
import os
from collections.abc import AsyncIterable
from typing import Any, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

from a2a_alert_agent.mcp_servers import ZMP_ALERT_OPENAPI_MCP_SERVER
from a2a_alert_agent.zmp_mcp_client_manager import ZmpMCPClientManager

memory = MemorySaver()


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class AlertAgent:
    """AlertAgent - a specialized assistant for alert management."""

    SYSTEM_INSTRUCTION = (
        "You are a specialized assistant for alert management. "
        "Your sole purpose is to use the 'get_alert' tool to answer questions about alert management. "
        "If the user asks about anything other than alert management, "
        "politely state that you cannot help with that topic and can only assist with alert management queries. "
        "Do not attempt to answer unrelated questions or use tools for other purposes."
    )

    FORMAT_INSTRUCTION = (
        "Set response status to input_required if the user needs to provide more information to complete the request."
        "Set response status to error if there is an error while processing the request."
        "Set response status to completed if the request is complete."
    )

    def __init__(self):
        """Initialize the AlertAgent."""

    @classmethod
    async def initialize(cls):
        """Initialize the AlertAgent."""
        instance = cls()
        model_source = os.getenv("model_source", "google")
        if model_source == "google":
            instance.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        else:
            instance.model = ChatOpenAI(
                model=os.getenv("TOOL_LLM_NAME"),
                openai_api_key=os.getenv("API_KEY", "EMPTY"),
                openai_api_base=os.getenv("TOOL_LLM_URL"),
                temperature=0,
            )

        instance.mcp_client_manager = await ZmpMCPClientManager.initialize()
        await instance.mcp_client_manager.add_mcp_servers(ZMP_ALERT_OPENAPI_MCP_SERVER)

        instance.tools = await instance.mcp_client_manager.get_tools()

        instance.graph = create_react_agent(
            instance.model,
            tools=instance.tools,
            checkpointer=memory,
            prompt=instance.SYSTEM_INSTRUCTION,
            response_format=(instance.FORMAT_INSTRUCTION, ResponseFormat),
        )
        return instance

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        """Stream the agent response."""
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": context_id}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Looking up alert information...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing alert data...",
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        """Get the agent response."""
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get("structured_response")
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message,
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": (
                "We are unable to process your request at the moment. Please try again."
            ),
        }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]


async def main():
    """Run the AlertAgent."""
    agent = await AlertAgent.initialize()
    print("AlertAgent initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
