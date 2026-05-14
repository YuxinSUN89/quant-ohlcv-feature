def signal(df, n, factor_name, config):
    # MtmVolMean indicator (Price momentum × volume momentum composite)
    # Formula: CLOSE_CHG = EMA(CLOSE/REF(CLOSE,N)-1, N) * 100
    #          VOL_CHG = EMA(QUOTE_VOLUME/REF(QUOTE_VOLUME,N)-1, N) * 100
    #          result = CLOSE_CHG * VOL_CHG
    # Combines EMA-smoothed price momentum with EMA-smoothed volume momentum.
    # Positive product = both price and volume trending in the same direction (confirming signal).
    df["close_change"] = (df["close"] / df["close"].shift(n) - 1).ewm(span=n, adjust=config.ewm_adjust).mean() * 100
    df["vol_change"] = (df["quote_volume"] / df["quote_volume"].shift(n) - 1).ewm(
        span=n, adjust=config.ewm_adjust
    ).mean() * 100

    df[factor_name] = df["close_change"] * df["vol_change"]

    return df
