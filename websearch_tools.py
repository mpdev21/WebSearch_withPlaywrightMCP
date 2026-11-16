"""Reusable LangChain tools and middleware for the WebSearch demos."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from langchain.agents.middleware import wrap_tool_call
from langchain_core.tools import BaseTool, tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from pydantic import BaseModel, Field

PROJECT_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = PROJECT_DIR / "screenshots"


@tool
def get_weather(city: str) -> str:
    """Return today's sample weather for a city."""
    weather_by_city = {
        "London": "rainy, 14 degrees",
        "Rome": "sunny, 27 degrees",
    }
    return weather_by_city.get(city, "clear, 20 degrees")


@tool
def get_population(city: str) -> str:
    """Return the sample population for a city."""
    population_by_city = {
        "London": "8.9 million",
        "Rome": "2.8 million",
    }
    return population_by_city.get(city, "unknown")


class CityReport(BaseModel):
    """Structured weather and population report for one city."""

    city: str = Field(description="The city name")
    weather: str = Field(description="A short weather description")
    population: str = Field(description="The population")


@wrap_tool_call
async def log_tool_calls(request, handler):
    """Log each tool call before passing it to the async handler."""
    call = request.tool_call
    print(f"  [middleware] calling {call['name']} with {call['args']}")
    return await handler(request)


@asynccontextmanager
async def browser_session() -> AsyncGenerator[list[BaseTool], None]:
    """Keep the Playwright MCP session alive while its tools are in use."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    client = MultiServerMCPClient({
        "playwright": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@playwright/mcp@latest",
                "--isolated",
                "--output-dir",
                str(SCREENSHOT_DIR),
            ],
            "cwd": str(PROJECT_DIR),
        }
    })
    async with client.session("playwright") as session:
        tools = await load_mcp_tools(session, server_name="playwright")
        yield tools
