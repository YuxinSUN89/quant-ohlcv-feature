import polars as pl


def signal(df, n, factor_name, config):
    # ChangeStd indicator (N-period return × rolling return std)
    # Formula: RTN = CLOSE.pct_change(); result = CLOSE.pct_change(N) * STD(RTN, N)
    # Combines directional momentum (N-period return) with recent volatility (rolling std of 1-period returns).
    # Acts as a risk-adjusted momentum measure: large returns in high-volatility environments are discounted.
    rtn = df["close"].pct_change()
    df = df.with_columns(
        pl.Series(
            factor_name,
            df["close"].pct_change(n) * rtn.rolling_std(n, min_samples=config.min_periods, ddof=config.ddof),
        )
    )

    return df
