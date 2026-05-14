import polars as pl


def signal(df, n, factor_name, config):
    # AbsChg indicator (Absolute N-period price change)
    # Formula: result = |CLOSE.pct_change(N)|
    # Measures the absolute magnitude of the N-period return regardless of direction.
    # High values indicate significant price moves; useful as a volatility proxy or for filtering signals.
    df = df.with_columns(pl.Series(factor_name, abs(df["close"].pct_change(n))))

    return df
