import polars as pl


def signal(df, n, factor_name, config):
    # VwapSignal indicator
    eps = config.eps
    """
    # N=20
    # Typical=(HIGH+LOW+CLOSE)/3
    # MF=VOLUME*Typical
    # VOLUME_SUM=SUM(VOLUME,N)
    # MF_SUM=SUM(MF,N)
    # VWAP=MF_SUM/VOLUME_SUM
    # VWAP computes the volume-weighted average price. Buy when current price crosses above VWAP; sell when it crosses below.
    """
    df = df.with_columns(pl.Series("tp", (df["high"] + df["low"] + df["close"]) / 3))
    df = df.with_columns(pl.Series("mf", df["volume"] * df["tp"]))
    df = df.with_columns(pl.Series("vol_sum", df["volume"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mf_sum", df["mf"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("vwap", df["mf_sum"] / (eps + df["vol_sum"])))
    df = df.with_columns(pl.Series(factor_name, df["tp"] / (df["vwap"] + eps) - 1))

    # remove redundant columns
    df = df.drop(["tp", "mf", "vol_sum", "mf_sum", "vwap"])

    return df
