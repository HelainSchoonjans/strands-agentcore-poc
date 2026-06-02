"""A basic reusable agent"""

import math
from typing import Annotated
from strands import Agent, tool

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
    """Creates and returns an agent with some basic math tools"""
    agent = Agent(tools=[cosine, sine, divide], model="qwen.qwen3-vl-235b-a22b")
    return agent