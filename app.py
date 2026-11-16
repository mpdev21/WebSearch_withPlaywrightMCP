"""Command-line entry point for the WebSearch agent examples."""

import argparse
import asyncio
from collections.abc import Awaitable, Callable

from dotenv import load_dotenv

from websearch import (
    run_all_demos,
    run_basic_demo,
    run_browser_demo,
    run_memory_demo,
    run_middleware_demo,
    run_structured_output_demo,
    run_tools_demo,
)

Demo = Callable[[], Awaitable[None]]

DEMOS: dict[str, Demo] = {
    "all": run_all_demos,
    "basic": run_basic_demo,
    "tools": run_tools_demo,
    "memory": run_memory_demo,
    "structured": run_structured_output_demo,
    "middleware": run_middleware_demo,
    "browser": run_browser_demo,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run WebSearch agent examples.")
    parser.add_argument(
        "--demo",
        choices=DEMOS,
        default="all",
        help="Choose one example to run (default: all examples).",
    )
    parser.add_argument(
        "--keep-browser-open",
        action="store_true",
        help="Keep the browser open after the browser demo until you press Enter.",
    )
    args = parser.parse_args()
    if args.keep_browser_open and args.demo not in {"all", "browser"}:
        parser.error("--keep-browser-open can only be used with --demo all or --demo browser.")
    return args


async def run(demo_name: str, *, keep_browser_open: bool = False) -> None:
    load_dotenv(override=True)
    if demo_name == "browser":
        await run_browser_demo(keep_browser_open=keep_browser_open)
    elif demo_name == "all":
        await run_all_demos(keep_browser_open=keep_browser_open)
    else:
        await DEMOS[demo_name]()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.demo, keep_browser_open=args.keep_browser_open))


if __name__ == "__main__":
    main()
