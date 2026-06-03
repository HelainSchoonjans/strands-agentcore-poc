"""A basic reusable agent"""

import math
from typing import Annotated
from strands import Agent, tool

import os
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

# Ensure your credentials are populated in the environment
env_config = {
    "JIRA_BASE_URL": os.getenv("JIRA_BASE_URL"),
    "JIRA_EMAIL": os.getenv("JIRA_EMAIL") or os.getenv("JIRA_USER_EMAIL"),
    "JIRA_USER_EMAIL": os.getenv("JIRA_USER_EMAIL"),
    "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN")
}

current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(current_dir, "node_modules", "@orengrinker", "jira-mcp-server", "dist", "index.js")

# 1. Initialize the MCP Client pointing to the Jira MCP server package
# We use 'node' to execute the locally installed server since the package lacks a bin mapping for 'npx'
jira_mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="node",
            args=[mcp_server_path],
            env=env_config
        )
    )
)

@tool(description="Calculates the cosine of x")
def cosine(x: Annotated[float, "The value of x in radians"]) -> float:
    """Cosine tool"""
    return math.cos(x)

@tool(description="Calculates the sine of x")
def sine(x: Annotated[float, "The value of x in radians"]) -> float:
    """Sine tool"""
    return math.sin(x)

@tool(description="Divides x by y")
def divide(x: Annotated[float, "The numerator"], y: Annotated[float, "The denominator"]) -> float:
    """Divide tool"""
    return x / y

def create_agent():
    # Start the MCP client manually if not already active
    if not jira_mcp_client._is_session_active():
        jira_mcp_client.start()

    # Discover all capabilities exposed by the server (e.g., search_issues, create_issue, add_comment)      
    jira_tools = jira_mcp_client.list_tools_sync()
    """Creates and returns an agent with some basic math tools and jira access"""
    agent = Agent(tools=[*jira_tools, cosine, sine, divide], model="qwen.qwen3-vl-235b-a22b")
    return agent
