import polars as pl


def signal(df, n, factor_name, config):
    # BIASVOL indicator
    """
    N=6，12，24
    BIASVOL(N)=(VOLUME-MA(VOLUME,N))/MA(VOLUME,N)
    BIASVOL is the volume version of the BIAS (deviation rate) indicator. A buy signal is
    generated when BIASVOL6 > 5 and BIASVOL12 > 7 and BIASVOL24 > 11;
    a sell signal is generated when BIASVOL6 < -5 and BIASVOL12 < -7 and BIASVOL24 < -11.
    """
    df = df.with_columns(pl.Series("ma_volume", df["volume"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["volume"] - df["ma_volume"]) / df["ma_volume"]))

    df = df.drop("ma_volume")

    return df
