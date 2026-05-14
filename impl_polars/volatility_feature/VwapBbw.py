import polars as pl


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
    width = df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods) * 2
    avg = df["close"].rolling_mean(n, min_samples=config.min_periods)
    top = avg + width
    bot = avg - width
    bbw = top / bot
    bbw_chg = bbw.pct_change(n)

    df = df.with_columns(
        pl.Series(
            "quote_volume_normalized",
            df["quote_volume"] / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods),
        )
    )

    feature = (vwap_chg * bbw_chg) / df["quote_volume_normalized"]
    df = df.with_columns(pl.Series(factor_name, feature.rolling_sum(n, min_samples=config.min_periods)))

    df = df.drop("quote_volume_normalized")

    return df
