import polars as pl


def signal(df, n, factor_name, config):
    # RocVol indicator
    """
    N = 80
    RocVol=(VOLUME-REF(VOLUME,N))/REF(VOLUME,N)
    RocVol is the volume version of ROC. Buy when RocVol crosses above 0;
    sell when it crosses below 0.
    """
    df = df.with_columns(pl.Series(factor_name, df["volume"] / (df["volume"].shift(n) + config.eps) - 1))

    return df
