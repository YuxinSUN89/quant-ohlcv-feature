import polars as pl


def signal(df, n, factor_name, config):
    # DiffEma indicator (Short EMA - Long EMA relative to its own EMA)
    # Formula: DIFF_EMA = EMA(CLOSE,N) - EMA(CLOSE,3N)
    #          result = DIFF_EMA / EMA(DIFF_EMA, N) - 1
    # Measures how the EMA spread (short minus long) compares to its own recent average.
    # Positive values indicate the spread is widening (accelerating trend); negative indicates narrowing (decelerating).
    short_windows = n
    long_windows = 3 * n
    df = df.with_columns(pl.Series("ema_short", df["close"].ewm_mean(span=short_windows, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_long", df["close"].ewm_mean(span=long_windows, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("diff_ema", df["ema_short"] - df["ema_long"]))

    df = df.with_columns(pl.Series("diff_ema_mean", df["diff_ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series(factor_name, df["diff_ema"] / df["diff_ema_mean"] - 1))

    df = df.drop("ema_short")
    df = df.drop("ema_long")
    df = df.drop("diff_ema")
    df = df.drop("diff_ema_mean")

    return df
