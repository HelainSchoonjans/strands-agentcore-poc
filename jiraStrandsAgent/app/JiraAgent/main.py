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


# Add MCP client to tools if available
for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)

def create_streamable_http_transport(mcp_url: str):
    if not mcp_url:
        raise ValueError(
            "Jira Gateway URL is missing. JIRA_GATEWAY_URL environment variable is not set, "
            "and no deployed gateway URL was found in agentcore/.cli/deployed-state.json. "
            "Please deploy your resources using 'agentcore deploy' first."
        )
    return streamablehttp_client(mcp_url)

def get_full_tools_list(client):
    """Get all tools with pagination support directly from your Jira Gateway"""
    more_tools = True
    tools_list = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools_list.extend(tmp_tools)
        if getattr(tmp_tools, "pagination_token", None) is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools_list

# When deployed, AgentCore automatically injects your gateway's URL 
# as an environment variable. Locally, it falls back to your 'agentcore status' value.
gateway_url = os.environ.get("JIRA_GATEWAY_URL")

if not gateway_url:
    import json
    from pathlib import Path
    current_dir = Path(__file__).parent.resolve()
    for parent in [current_dir] + list(current_dir.parents):
        state_file = parent / "agentcore" / ".cli" / "deployed-state.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                targets = data.get("targets", {})
                for target_name, target_data in targets.items():
                    resources = target_data.get("resources", {})
                    mcp = resources.get("mcp", {})
                    gateways = mcp.get("gateways", {})
                    for gw_name, gw_data in gateways.items():
                        url = gw_data.get("gatewayUrl")
                        if url:
                            gateway_url = url
                            break
                    if gateway_url:
                        break
            except Exception:
                pass
        if gateway_url:
            break

# Name specifically to prevent variable collision and shadowing
jira_mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url))



def agent_factory():
    cache = {}
    def get_or_create_agent(session_id, user_id):
        key = f"{session_id}/{user_id}"
        if key not in cache:
            def create_agent():
                # Pull down the paginated Jira tool definitions (create_ticket, etc.)
                jira_tools = get_full_tools_list(jira_mcp_client)
                # Safely merge global tools with dynamic JIRA tools
                combined_tools = list(tools) + list(jira_tools)
                # Create an agent for the given session_id and user_id
                cache[key] = Agent(
                    model=load_model(),
                    session_manager=get_memory_session_manager(session_id, user_id),
                    system_prompt=DEFAULT_SYSTEM_PROMPT,
                    tools=combined_tools
                )
            
            if jira_mcp_client._is_session_active():
                create_agent()
            else:
                with jira_mcp_client:
                    create_agent()
        return cache[key]
    return get_or_create_agent
get_or_create_agent = agent_factory()


@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Agent.....")

    session_id = getattr(context, 'session_id', 'default-session')
    user_id = getattr(context, 'user_id', 'default-user')
    
    with jira_mcp_client:
        agent = get_or_create_agent(session_id, user_id)

        # Execute and format response
        stream = agent.stream_async(payload.get("prompt"))

        async for event in stream:
            # Handle Text parts of the response
            if "data" in event and isinstance(event["data"], str):
                yield event["data"]


if __name__ == "__main__":
    app.run()
