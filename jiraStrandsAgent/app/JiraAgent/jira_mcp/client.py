import os
import json
import logging
from pathlib import Path
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

def create_streamable_http_transport(mcp_url: str):
    if not mcp_url:
        raise ValueError(
            "Jira Gateway URL is missing. Neither AGENTCORE_GATEWAY_JIRAGATEWAY_URL "
            "nor JIRA_GATEWAY_URL environment variables are set, and no deployed "
            "gateway URL was found in agentcore/.cli/deployed-state.json. "
            "Please deploy your resources using 'agentcore deploy' first."
        )
    return streamablehttp_client(mcp_url)

def get_full_tools_list(client: MCPClient):
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
# as an environment variable (using the format AGENTCORE_GATEWAY_{GATEWAY_NAME}_URL).
# Locally, it falls back to your 'agentcore status' value.
gateway_url = os.environ.get("AGENTCORE_GATEWAY_JIRAGATEWAY_URL") or os.environ.get("JIRA_GATEWAY_URL")

if not gateway_url:
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
            except Exception as e:
                logger.warning(f"Failed to read deployed-state.json: {e}")
                pass
        if gateway_url:
            break

# Name specifically to prevent variable collision and shadowing
jira_mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url))
