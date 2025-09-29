import yfinance as yf
from mcp.server.fastmcp import FastMCP

# Create the MCP instance
mcp = FastMCP("StockPrice")

@mcp.tool()
def get_stock_price(ticker: str, period: str = "1d", interval: str = "1h") -> dict:
    """
    Fetch recent stock price data for a given ticker symbol using yfinance.

    Args:
        ticker: The stock ticker symbol (e.g. 'AAPL', 'GOOG', 'TSLA').
        period: Time period for which to fetch data (default: '1d').
                Supported values: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        interval: Data granularity (default: '1h').
                  Supported values: '1m', '2m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'

    Returns:
        A dictionary containing:
            - ticker
            - current price
            - open, high, low, close
            - timestamp of last data point
    """
    ticker_obj = yf.Ticker(ticker)
    data = ticker_obj.history(period=period, interval=interval)

    if data.empty:
        return {"error": f"No data found for ticker '{ticker}'."}

    last_row = data.iloc[-1]
    return {
        "ticker": ticker.upper(),
        "timestamp": str(last_row.name),
        "open": round(float(last_row["Open"]), 2),
        "high": round(float(last_row["High"]), 2),
        "low": round(float(last_row["Low"]), 2),
        "close": round(float(last_row["Close"]), 2),
        "volume": int(last_row["Volume"]),
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")