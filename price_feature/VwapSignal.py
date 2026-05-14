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
    df["tp"] = df[["high", "low", "close"]].sum(axis=1) / 3
    df["mf"] = df["volume"] * df["tp"]
    df["vol_sum"] = df["volume"].rolling(n, min_periods=config.min_periods).sum()
    df["mf_sum"] = df["mf"].rolling(n, min_periods=config.min_periods).sum()
    df["vwap"] = df["mf_sum"] / (eps + df["vol_sum"])
    df[factor_name] = df["tp"] / (df["vwap"] + eps) - 1

    # remove redundant columns
    del df["tp"], df["mf"], df["vol_sum"], df["mf_sum"], df["vwap"]

    return df
