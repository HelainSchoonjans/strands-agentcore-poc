from typing import Any

from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from mcp_client.client import get_streamable_http_mcp_client
from memory.session import get_memory_session_manager
# needed to use the JIRA gateway
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import os

app = BedrockAgentCoreApp()
log = app.logger

# Define a Streamable HTTP MCP Client
mcp_clients = [get_streamable_http_mcp_client()]

DEFAULT_SYSTEM_PROMPT ="""You are a helpful engineering assistant integrated into Jira Cloud. 
Your job is to read, create, update, and transition tickets based on user requests. 
Always double-check missing required parameters (like Issue Type or Project Key) 
by asking the user before making an API call."""


# Define a collection of tools used by the model
tools = []

# Define a simple function tool
@tool
def add_numbers(a: int, b: int) -> int:
    """Return the sum of two numbers"""
    return a+b
tools.append(add_numbers)


def create_streamable_http_transport(mcp_url: str):
    return streamablehttp_client(mcp_url)

def get_full_tools_list(client):
    """Get all tools with pagination support directly from your Jira Gateway"""
    more_tools = True
    tools = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if getattr(tmp_tools, "pagination_token", None) is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools
    
# When deployed, AgentCore automatically injects your gateway's URL 
# as an environment variable. Locally, it falls back to your 'agentcore status' value.
gateway_url = os.environ.get("JIRA_GATEWAY_URL", "<YOUR_GATEWAY_URL>")

# 2. Automatically discover and load the tools bridged by your JiraCloud gateway target
# 3. Establish the secure MCP block to resolve your Jira tools
mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url))
# AgentCore dynamically maps the OpenAPI spec into executable Python/TypeScript tools
#jira_tools = get_jira_tools()
#tools.extend(jira_tools)


# Add MCP client to tools if available
for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)


def agent_factory():
    cache = {}
    def get_or_create_agent(session_id, user_id):
        key = f"{session_id}/{user_id}"
        if key not in cache:
            with mcp_client:
                # Pull down the paginated Jira tool definitions (create_ticket, etc.)
                tools = get_full_tools_list(mcp_client)
                # Create an agent for the given session_id and user_id
                cache[key] = Agent(
                    model=load_model(),
                    session_manager=get_memory_session_manager(session_id, user_id),
                    system_prompt=DEFAULT_SYSTEM_PROMPT,
                    tools=tools
                )
        return cache[key]
    return get_or_create_agent
get_or_create_agent = agent_factory()


@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Agent.....")

    session_id = getattr(context, 'session_id', 'default-session')
    user_id = getattr(context, 'user_id', 'default-user')
    agent = get_or_create_agent(session_id, user_id)

    # Execute and format response
    stream = agent.stream_async(payload.get("prompt"))

    async for event in stream:
        # Handle Text parts of the response
        if "data" in event and isinstance(event["data"], str):
            yield event["data"]


if __name__ == "__main__":
    app.run()
