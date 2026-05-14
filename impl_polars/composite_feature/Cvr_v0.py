import polars as pl


def signal(df, n, factor_name, config):
    eps = config.eps
    # Cvr_v0 indicator (Calmar-Volume Ratio)
    # Formula: CVR = (SUM(PCT_CHANGE, N) / STD(PCT_CHANGE, N)) * (QUOTE_VOLUME / MA(QUOTE_VOLUME, N))
    #          result = MA(CVR, N)
    # Combines a risk-adjusted return measure (cumulative return / volatility, similar to Sharpe ratio)
    # with relative quote volume. High values indicate strong risk-adjusted momentum backed by above-average volume.
    df = df.with_columns(pl.Series("pc", df["close"].pct_change()))
    df = df.with_columns(pl.Series("vol", df["pc"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)))
    df = df.with_columns(pl.Series("ret", df["pc"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series(
            "cvr",
            (df["ret"] / (df["vol"] + eps))
            * (df["quote_volume"] / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["cvr"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.drop(["pc", "vol", "ret", "cvr"])

    return df
