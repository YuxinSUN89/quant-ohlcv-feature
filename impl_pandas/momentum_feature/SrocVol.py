def signal(df, n, factor_name, config):
    # SrocVol indicator (SROC applied to volume)
    # Formula: EMAP = EMA(VOLUME, 2N); result = (EMAP - REF(EMAP, N)) / REF(EMAP, N)
    # Measures the N-period rate of change of the long EMA of volume.
    # Positive values indicate volume trend is accelerating upward; negative indicates it's declining.
    # EMAP=EMA(VOLUME,N)
    df["emap"] = df["volume"].ewm(span=2 * n, adjust=config.ewm_adjust).mean()
    # SROCVOL=(EMAP-REF(EMAP,M))/REF(EMAP,M)
    df[factor_name] = (df["emap"] - df["emap"].shift(n)) / df["emap"].shift(n)

    del df["emap"]

    return df
