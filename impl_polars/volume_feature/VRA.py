import polars as pl


def signal(df, n, factor_name, config):
    # VRA indicator (Volatility-adjusted Rate of change composite)
    # Formula: RC = 100 * ((HIGH - REF(HIGH,N)) / REF(CLOSE,N) + (CLOSE - REF(CLOSE,2N)) / REF(LOW,2N))
    #          RC_MEAN = MA(RC, N); VOLATILITY = STD(CLOSE,N) / MA(CLOSE,N) * 100
    #          VRA = RC_MEAN * VOLATILITY
    # Combines a dual-window price rate-of-change (using high and close) with rolling price volatility.
    # Higher values suggest strong trending momentum accompanied by elevated volatility.
    df = df.with_columns(pl.Series("n_day_avg_price", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series("n_day_std", df["close"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof))
    )
    df = df.with_columns(pl.Series("n_day_volatility", df["n_day_std"] / df["n_day_avg_price"] * 100))
    # calculate upper and lower bands
    df = df.with_columns(
        pl.Series(
            "RC",
            100
            * (
                (df["high"] - df["high"].shift(n)) / (df["close"].shift(n) + config.eps)
                + (df["close"] - df["close"].shift(2 * n)) / df["low"].shift(2 * n)
            ),
        )
    )
    df = df.with_columns(pl.Series("RC_mean", df["RC"].rolling_mean(n, min_samples=config.min_periods)))

    # combined indicator
    df = df.with_columns(pl.Series(factor_name, df["RC_mean"] * df["n_day_volatility"]))

    df = df.drop(["n_day_avg_price", "n_day_std", "RC"])

    return df
