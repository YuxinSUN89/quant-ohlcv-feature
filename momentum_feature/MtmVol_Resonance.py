def signal(df, n, factor_name, config):
    # MtmVol_Resonance indicator (MTM mean × volume change mean)
    # Formula: MTM_MEAN = MA(CLOSE/REF(CLOSE,N)-1, N)
    #          VOL_CHG = QUOTE_VOLUME / MA(QUOTE_VOLUME,N); VOL_CHG_MEAN = MA(VOL_CHG, N)
    #          result = MTM_MEAN * VOL_CHG_MEAN
    # Resonance between price momentum and relative volume activity.
    # High values indicate sustained price momentum coinciding with above-average trading volume.
    df["mtm"] = df["close"] / df["close"].shift(n) - 1
    df["mtm_mean"] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean()

    df["quote_volume_mean"] = df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    df["quote_volume_change"] = df["quote_volume"] / df["quote_volume_mean"]
    df["quote_volume_change_mean"] = df["quote_volume_change"].rolling(n, min_periods=config.min_periods).mean()

    df[factor_name] = df["mtm_mean"] * df["quote_volume_change_mean"]

    drop_col = ["mtm", "mtm_mean", "quote_volume_mean", "quote_volume_change", "quote_volume_change_mean"]
    df.drop(columns=drop_col, inplace=True)

    return df
