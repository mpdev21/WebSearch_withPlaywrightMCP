"""Runnable examples demonstrating LangChain agents and Playwright MCP."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from IPython.display import Image, display
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from websearch_tools import (
    CityReport,
    PROJECT_DIR,
    browser_session,
    get_population,
    get_weather,
    log_tool_calls,
)

MODEL = "openai:gpt-5.4-mini"
TRAVEL_PROMPT = "You are a travel assistant. Use your tools to answer questions about cities."


async def run_basic_demo() -> None:
    """Create an agent without tools and ask two questions."""
    agent = create_agent(
        model=MODEL,
        system_prompt="You are a helpful assistant who answers concisely.",
    )
    questions = (
        "What is the Model Context Protocol, in two sentences?",
        "In one sentence: why does async code suit agents so well?",
    )
    for question in questions:
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        print(result["messages"][-1].content)


async def run_tools_demo() -> None:
    """Use sample weather and population tools to answer a question."""
    agent = create_agent(
        model=MODEL,
        tools=[get_weather, get_population],
        system_prompt=TRAVEL_PROMPT,
    )
    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "What is the weather and population of Rome?",
        }]
    })
    print(result["messages"][-1].content)
    display(Image(agent.get_graph().draw_mermaid_png()))


async def run_memory_demo() -> None:
    """Show that a checkpointer retains context across turns."""
    agent = create_agent(
        model=MODEL,
        tools=[get_weather],
        checkpointer=MemorySaver(),
        system_prompt=TRAVEL_PROMPT,
    )
    config = {"configurable": {"thread_id": "trip-planning"}}
    await agent.ainvoke({
        "messages": [{"role": "user", "content": "I am planning a trip to London."}]
    }, config=config)
    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "What is the weather like where I am going on my trip?",
        }]
    }, config=config)
    print(result["messages"][-1].content)


async def run_structured_output_demo() -> None:
    """Return a Pydantic model rather than an unstructured answer."""
    agent = create_agent(
        model=MODEL,
        tools=[get_weather, get_population],
        response_format=CityReport,
    )
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Give me a report on London."}]
    })
    report = result["structured_response"]
    print(report)
    print("Just the weather:", report.weather)


async def run_middleware_demo() -> None:
    """Log calls made by an agent's tools."""
    agent = create_agent(
        model=MODEL,
        tools=[get_weather, get_population],
        system_prompt="You are a travel assistant. Use your tools.",
        middleware=[log_tool_calls],
    )
    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "Weather and population of London and Rome?",
        }]
    })
    print("\nFinal answer:", result["messages"][-1].content)


async def run_browser_demo(*, keep_browser_open: bool = False) -> None:
    """Use Playwright MCP to research Hacker News and save a screenshot."""
    screenshot_path = PROJECT_DIR / "screenshots" / "hacker-news.png"

    async with browser_session() as browser_tools:
        tools_by_name = {browser_tool.name: browser_tool for browser_tool in browser_tools}
        navigate = tools_by_name.get("browser_navigate")
        take_screenshot = tools_by_name.get("browser_take_screenshot")
        if navigate is None or take_screenshot is None:
            raise RuntimeError(
                "The Playwright MCP server must provide browser_navigate and "
                "browser_take_screenshot tools."
            )

        print(f"Loaded {len(browser_tools)} browser tools.")
        await navigate.ainvoke({"url": "https://news.ycombinator.com"})

        agent = create_agent(
            model="openai:gpt-5.5",
            tools=browser_tools,
            system_prompt=(
                "You are a web research assistant. Use the browser tools to complete "
                "the task, then report clearly."
            ),
        )
        result = await agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": (
                    "Read the front page of https://news.ycombinator.com and report "
                    "the titles of its top three stories."
                ),
            }]
        })
        print(result["messages"][-1].content)

        await take_screenshot.ainvoke({
            "filename": str(Path("screenshots") / screenshot_path.name),
            "scale": "css",
        })
        if not screenshot_path.is_file() or screenshot_path.stat().st_size == 0:
            raise RuntimeError(f"Playwright did not save the screenshot to {screenshot_path}.")
        print(f"Screenshot saved to: {screenshot_path}")

        if keep_browser_open:
            await asyncio.to_thread(input, "Browser is still open. Press Enter to close it...")


async def run_all_demos(*, keep_browser_open: bool = False) -> None:
    """Run all examples in their teaching order."""
    demos = (
        run_basic_demo,
        run_tools_demo,
        run_memory_demo,
        run_structured_output_demo,
        run_middleware_demo,
        run_browser_demo,
    )
    for demo in demos[:-1]:
        print(f"\n== {demo.__doc__} ==")
        await demo()
    print(f"\n== {run_browser_demo.__doc__} ==")
    await run_browser_demo(keep_browser_open=keep_browser_open)


if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(run_all_demos())
