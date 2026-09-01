def signal(*args):
    # EmaFilter indicator (EMA(close) minus EMA(open) spread)
    # Formula: EmaFilter = EMA(CLOSE, n) - EMA(OPEN, n); n defaults to 13
    # Compares an EMA of the close series to an EMA of the open series.
    # Positive and widening values suggest sustained intraday buying pressure building up over the window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 13
    close_ema = df['close'].ewm(span=n, adjust=False).mean()
    open_ema = df['open'].ewm(span=n, adjust=False).mean()
    df[factor_name] = close_ema - open_ema

    return df
