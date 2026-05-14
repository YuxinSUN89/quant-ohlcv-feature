import polars as pl


def signal(df, n, factor_name, config):
    # VIDYA
    """
    N=10
    VI=ABS(CLOSE-REF(CLOSE,N))/SUM(ABS(CLOSE-REF(CLOSE,1)),N)
    VIDYA=VI*CLOSE+(1-VI)*REF(CLOSE,1)
    VIDYA is a type of moving average, but its weights incorporate the ER
    (Efficiency Ratio) indicator. When the current trend is strong, ER is large and VIDYA
    gives more weight to the current price, making VIDYA closely track price changes and
    reducing its lag. When the trend is weak (e.g., in a ranging market), ER is small and
    VIDYA gives less weight to the current price, increasing its lag to make it smoother
    and avoiding excessive trading signals.
    Buy/sell signals are generated when the closing price crosses above/below VIDYA.
    """
    _ts = (df["open"] + df["close"]) / 2.0

    vi = (_ts - _ts.shift(n)).abs() / (_ts - _ts.shift(1)).abs().rolling_sum(n, min_samples=config.min_periods)
    vidya = vi * _ts + (1 - vi) * _ts.shift(1)

    # normalize
    df = df.with_columns(pl.Series(factor_name, vidya / df["close"]))

    return df
