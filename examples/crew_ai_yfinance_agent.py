import os
from typing import Optional
import yaml

from crewai import Agent, Crew, Task
from crewai_tools import MCPServerAdapter
from pydantic import BaseModel, Field
from agentics import AG
from mcp import StdioServerParameters


# -------------------------
# Pydantic Models
# -------------------------

class StockPrice(BaseModel):
    ticker: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockReport(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    stock_data: Optional[StockPrice] = None
    notes: Optional[str] = Field(
        None, description="Any additional commentary or interpretation."
    )


# -------------------------
# Connect MCP Servers
# -------------------------

yfinance_params = StdioServerParameters(
    command="python3",
    args=[os.getenv("MCP_SERVER_PATH")],  # Path to your yfinance MCP server script
    env={"UV_PYTHON": "3.12", **os.environ},
)

with MCPServerAdapter(yfinance_params) as yfinance_tools:
    print(f"Available tools from YFinance MCP server: {[tool.name for tool in yfinance_tools]}")

    tools = yfinance_tools

    # -------------------------
    # Agent Definition
    # -------------------------
    stock_agent = Agent(
        role="Stock Analyst",
        goal="Retrieve and summarize the latest stock price data for a given ticker.",
        backstory="A financial assistant that uses the YFinance MCP server to fetch stock data.",
        tools=tools,
        reasoning=False,
        memory=False,
        verbose=True,
        llm=AG.get_llm_provider(),
    )

    # -------------------------
    # Task Definition
    # -------------------------
    stock_task = Task(
        description="""
        Fetch and summarize the latest stock price for {ticker}.
        Include open, close, high, low, and volume data.
        """,
        expected_output="A structured StockReport object containing latest price data and a summary.",
        agent=stock_agent,
        output_pydantic=StockReport,
    )

    crew = Crew(
        agents=[stock_agent],
        tasks=[stock_task],
        verbose=True,
    )

    # -------------------------
    # Run Crew
    # -------------------------
    result = crew.kickoff(inputs={"ticker": "AAPL"})  # Example ticker

    if result.pydantic:
        print(yaml.dump(result.pydantic.model_dump(), sort_keys=False))
    else:
        print("No result produced.")
