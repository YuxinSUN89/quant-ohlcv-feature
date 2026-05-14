import polars as pl


def signal(df, n, factor_name, config):
    # MACDVOL indicator
    """
    N1=20
    N2=40
    N3=10
    MACDVOL=EMA(VOLUME,N1)-EMA(VOLUME,N2)
    SIGNAL=MA(MACDVOL,N3)
    MACDVOL is the volume version of MACD. Buy when MACDVOL crosses above SIGNAL;
    sell when it crosses below SIGNAL.
    """
    N1 = 2 * n
    N2 = 4 * n
    N3 = n
    df = df.with_columns(pl.Series("ema_volume_1", df["volume"].ewm_mean(span=N1, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_volume_2", df["volume"].ewm_mean(span=N2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("MACDV", df["ema_volume_1"] - df["ema_volume_2"]))
    df = df.with_columns(pl.Series("SIGNAL", df["MACDV"].rolling_mean(N3, min_samples=config.min_periods)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["MACDV"] / df["SIGNAL"] - 1))

    df = df.drop("ema_volume_1")
    df = df.drop("ema_volume_2")
    df = df.drop("MACDV")
    df = df.drop("SIGNAL")

    return df
