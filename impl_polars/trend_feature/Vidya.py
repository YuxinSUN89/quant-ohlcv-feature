import polars as pl


def signal(df, n, factor_name, config):
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
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
    df = df.with_columns(
        pl.Series("abs_diff_close", (df["close"] - df["close"].shift(1)).abs())
    )  # ABS(CLOSE-REF(CLOSE,1))
    df = df.with_columns(
        pl.Series("abs_diff_close_n", (df["close"] - df["close"].shift(n)).abs())
    )  # ABS(CLOSE-REF(CLOSE,N))
    df = df.with_columns(
        pl.Series("abs_diff_close_sum", df["abs_diff_close"].rolling_sum(n, min_samples=config.min_periods))
    )  # SUM(ABS(CLOSE-REF(CLOSE,1))
    # VI=ABS(CLOSE-REF(CLOSE,N))/SUM(ABS(CLOSE-REF(CLOSE,1)),N)
    VI = df["abs_diff_close_n"] / df["abs_diff_close_sum"]
    # VIDYA=VI*CLOSE+(1-VI)*REF(CLOSE,1)
    VIDYA = VI * df["close"] + (1 - VI) * df["close"].shift(1)
    # normalize
    df = df.with_columns(
        pl.Series(factor_name, VIDYA / df["close"].rolling_mean(n, min_samples=config.min_periods) - 1)
    )

    df = df.drop("abs_diff_close")
    df = df.drop("abs_diff_close_n")
    df = df.drop("abs_diff_close_sum")

    return df
