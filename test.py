import time

import httpx
import pandas as pd
import yfinance as yf


# --- 1. 加密货币: Binance (无需API Key) ---
def fetch_binance_klines(symbol: str, interval: str, limit: int = 10):
    """
    从币安获取K线数据 (REST API)。
    精度: 最高1分钟线。更实时的数据需要用WebSocket。
    """
    print(f"\n--- [Crypto via Binance] Fetching {symbol} ({interval}) ---")
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        df = pd.DataFrame(
            data,
            columns=[
                "Open Time",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "Close Time",
                "Quote Asset Volume",
                "Number of Trades",
                "Taker Buy Base Asset Volume",
                "Taker Buy Quote Asset Volume",
                "Ignore",
            ],
        )
        df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        print("Data successfully fetched:")
        print(df[["Open Time", "Open", "High", "Low", "Close", "Volume"]])
    except Exception as e:
        print(f"Error fetching from Binance: {e}")


# --- 2. 股票 & 期货: Yahoo Finance (无需API Key) ---
def fetch_yfinance_data(
    ticker: str, name: str, period: str = "1mo", interval: str = "1d"
):
    """
    使用 yfinance 从雅虎财经获取股票或期货数据。
    精度: 股票延迟约15分钟，期货延迟10-15分钟。分钟级数据可能不适用于所有品种。
    """
    print(f"\n--- [Stocks/Futures via Yahoo Finance] Fetching {name} ({ticker}) ---")
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            print(
                f"No data found for {ticker}. Check the symbol or try a different period/interval."
            )
            return
        print("Data successfully fetched:")
        print(hist.tail())  # 打印最后几行数据
    except Exception as e:
        print(f"Error fetching from yfinance for {ticker}: {e}")


# --- 3. 外汇 (Forex): Alpha Vantage (需要免费API Key) ---
def fetch_alphavantage_forex_daily(from_symbol: str, to_symbol: str, api_key: str):
    """
    从 Alpha Vantage 获取每日外汇数据。
    精度: 免费版提供日线数据。
    """
    print(f"\n--- [Forex via Alpha Vantage] Fetching {from_symbol}/{to_symbol} ---")
    if not api_key or api_key == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Alpha Vantage API Key is missing. Please provide a valid key.")
        return

    url = (
        f"https://www.alphavantage.co/query?function=FX_DAILY"
        f"&from_symbol={from_symbol}&to_symbol={to_symbol}"
        f"&apikey={api_key}"
    )
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()

        if "Time Series FX (Daily)" not in data:
            print(
                "Error fetching from Alpha Vantage. The API may have returned an error or reached its limit."
            )
            print("Response:", data)
            return

        df = pd.DataFrame.from_dict(data["Time Series FX (Daily)"], orient="index")
        df.columns = ["Open", "High", "Low", "Close"]
        df.index = pd.to_datetime(df.index)
        df = df.astype(float).sort_index(ascending=False)
        print("Data successfully fetched (showing recent days):")
        print(df.head())
    except Exception as e:
        print(f"Error fetching from Alpha Vantage: {e}")


if __name__ == "__main__":
    # --- 1. 测试加密货币 (Binance) ---
    fetch_binance_klines(symbol="ETHUSDT", interval="1h", limit=5)
    time.sleep(1)  # 友好等待

    # --- 2. 测试股票 (Yahoo Finance) ---
    # 美股: 苹果 (AAPL)
    fetch_yfinance_data(ticker="AAPL", name="Apple Inc.", period="1mo", interval="1d")
    time.sleep(2)  # 友好等待
    # A股: 贵州茅台 (代码需加 .SS 后缀)
    fetch_yfinance_data(
        ticker="600519.SS", name="Kweichow Moutai", period="1mo", interval="1d"
    )
    time.sleep(2)

    # --- 3. 测试期货 (Yahoo Finance) ---
    # WTI原油期货 (CL=F)
    fetch_yfinance_data(
        ticker="CL=F", name="Crude Oil Futures", period="1mo", interval="1d"
    )
    time.sleep(2)
    # S&P 500 E-mini 期货 (ES=F)
    fetch_yfinance_data(
        ticker="ES=F", name="S&P 500 E-mini Futures", period="1mo", interval="1d"
    )
    time.sleep(2)

    # --- 4. 测试外汇 (Alpha Vantage) ---
    # !! 重要: 请替换成你自己的免费API Key !!
    alpha_vantage_key = "YOUR_ALPHA_VANTAGE_API_KEY"
    fetch_alphavantage_forex_daily(
        from_symbol="EUR", to_symbol="USD", api_key=alpha_vantage_key
    )
