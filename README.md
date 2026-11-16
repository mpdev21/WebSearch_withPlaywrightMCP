# WebSearch_withPlaywrightMCP
Building a Web Search with Agent with create_agent and Playwright MCP

## Setup

Install the Python dependencies into a project virtual environment:

```bash
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Set `OPENAI_API_KEY` in a `.env` file in this directory. The Playwright MCP
examples also require Node.js and `npx`.

Run all examples from the project environment:

```bash
.venv/bin/python app.py
```

Run one example at a time with `--demo`: `basic`, `tools`, `memory`,
`structured`, `middleware`, or `browser`. For example:

```bash
.venv/bin/python app.py --demo browser
```

The browser demo keeps one Playwright MCP session open for the entire run and
saves a screenshot to `screenshots/hacker-news.png`. To leave the headed browser
open after the screenshot is saved, run:

```bash
.venv/bin/python app.py --demo browser --keep-browser-open
```

Press Enter in the terminal to close the browser and finish the program.

`websearch.py` contains the demo functions and can also run the full sequence
directly. `websearch_tools.py` contains reusable tool and middleware definitions.
