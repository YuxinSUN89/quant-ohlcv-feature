import polars as pl


def signal(df, n, factor_name, config):
    # RetBoll_fancy indicator (Bollinger Bands applied to returns / z-score of returns)
    # Formula: RTN = CLOSE.pct_change(); result = (RTN - MA(RTN,N)) / STD(RTN,N)
    # Applies z-score normalization to the return series rather than the price series.
    # Measures how extreme the current return is relative to recent return history.
    # High positive values indicate unusually strong up moves; high negative values indicate down moves.
    df = df.with_columns(pl.Series("_ret", df["close"].pct_change()))
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["_ret"] - df["_ret"].rolling_mean(n, min_samples=config.min_periods))
            / df["_ret"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof),
        ).fill_nan(None)
    )

    df = df.drop("_ret")

    return df
