import talib as ta


def signal(df, n, factor_name, config):
    # Acs indicator (Rolling std of ADX/close ratio)
    # Formula: ADX_CLOSE = ADX(N) / CLOSE; result = STD(ADX_CLOSE, N)
    # ADX measures trend strength; dividing by close normalizes for price level.
    # The rolling std captures how consistently ADX/close has been varying (volatility of trend strength).
    # Numerical sensitivity note:
    # Acs depends on TA-Lib ADX plus a rolling standard deviation of a normalized series.
    # Small input float / CSV-parsing differences can survive through ADX and show up as tiny
    # residual drift in the final rolling std statistics.
    df["adx"] = ta.ADX(df["high"], df["low"], df["close"], n)
    df["adx_close"] = df["adx"] / df["close"]
    df[factor_name] = df["adx_close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)

    del df["adx"], df["adx_close"]

    return df
