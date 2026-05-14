def signal(df, n, factor_name, config):
    # VwapBbw indicator (VWAP change × BBW change / normalized quote volume)
    # Formula: VWAP = QUOTE_VOLUME / VOLUME; VWAP_CHG = VWAP.pct_change(N)
    #          BBW = (MA + 2*STD) / (MA - 2*STD); BBW_CHG = BBW.pct_change(N)
    #          result = SUM(VWAP_CHG * BBW_CHG / (QUOTE_VOLUME / MA(QUOTE_VOLUME,N)), N)
    # Combines VWAP momentum, Bollinger bandwidth expansion, and inverse volume normalization.
    # Captures price efficiency relative to volume: high values indicate VWAP trending with expanding
    # volatility but relatively low volume (efficient trend with less market participation).
    vwap = df["quote_volume"] / df["volume"]
    vwap_chg = vwap.pct_change(n)
    # calculate rate of change of width
    width = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof) * 2
    avg = df["close"].rolling(n, min_periods=config.min_periods).mean()
    top = avg + width
    bot = avg - width
    bbw = top / bot
    bbw_chg = bbw.pct_change(n)

    df["quote_volume_normalized"] = (
        df["quote_volume"] / df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    )

    feature = (vwap_chg * bbw_chg) / df["quote_volume_normalized"]
    df[factor_name] = feature.rolling(n, min_periods=config.min_periods).sum()

    del df["quote_volume_normalized"]

    return df
