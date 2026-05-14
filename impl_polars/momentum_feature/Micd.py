import polars as pl


def signal(df, n, factor_name, config):
    # MICD indicator
    """
    N=20
    N1=10
    N2=20
    M=10
    MI=CLOSE-REF(CLOSE,1)
    MTMMA=SMA(MI,N,1)
    DIF=MA(REF(MTMMA,1),N1)-MA(REF(MTMMA,1),N2)
    MICD=SMA(DIF,M,1)
    A buy signal is generated when MICD crosses above 0;
    a sell signal is generated when MICD crosses below 0.
    """
    df = df.with_columns(pl.Series("MI", df["close"] - df["close"].shift(1)))
    df = df.with_columns(pl.Series("MIMMA", df["MI"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("MIMMA_MA1", df["MIMMA"].shift(1).rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series("MIMMA_MA2", df["MIMMA"].shift(1).rolling_mean(2 * n, min_samples=config.min_periods))
    )
    df = df.with_columns(pl.Series("DIF", df["MIMMA_MA1"] - df["MIMMA_MA2"]))
    df = df.with_columns(pl.Series("MICD", df["DIF"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["DIF"] / df["MICD"]))

    df = df.drop("MI")
    df = df.drop("MIMMA")
    df = df.drop("MIMMA_MA1")
    df = df.drop("MIMMA_MA2")
    df = df.drop("DIF")
    df = df.drop("MICD")

    return df
