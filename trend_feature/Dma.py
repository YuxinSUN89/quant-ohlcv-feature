import talib as ta


def signal(df, n, factor_name, config):
    # Dma indicator (ATR-scaled MA difference)
    # Formula: ATR_X = ATR(N) / SUM(ATR,N); MA_SHORT = MA(CLOSE,N); MA_LONG = MA(CLOSE,2N)
    #          MA_DIF = MA_SHORT - MA_LONG; DMA = MA_DIF / SUM(|MA_DIF|,2N) + 1
    #          result = DMA * (1 + ATR_X)
    # Combines a normalized MA crossover signal with ATR volatility weighting.
    # Values above 1 suggest upward-trending regime; amplified further in high-volatility periods.
    atr = ta.ATR(df["high"], df["low"], df["close"], timeperiod=n)
    atr_x = atr / atr.rolling(n, min_periods=config.min_periods).sum()

    ma_short = df["close"].rolling(n, min_periods=config.min_periods).mean()
    ma_long = df["close"].rolling(2 * n, min_periods=config.min_periods).mean()
    ma_dif = ma_short - ma_long
    dma = (ma_dif / abs(ma_dif).rolling(2 * n, min_periods=config.min_periods).sum()) + 1
    df[factor_name] = dma * (1 + atr_x)

    return df
