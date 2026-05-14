import polars as pl


def signal(df, n, factor_name, config):
    # MtmTb indicator (Momentum mean × Taker buy ratio)
    # Formula: MTM_MEAN = EMA(CLOSE/REF(CLOSE,N)-1, N)
    #          TAKER_BUY_MA = MA(taker_buy_quote / MA(quote_volume,N) * 100, N)
    #          result = MTM_MEAN * TAKER_BUY_MA
    # Multiplies EMA-smoothed price momentum by the average taker buy pressure (as % of volume).
    # High positive values indicate strong upside momentum backed by buyer-initiated trades.
    # df['tr_trix'] = df['close'].ewm_mean(span=n, adjust=config.ewm_adjust)
    # df['tr_pct'] = df['tr_trix'].pct_change()
    # average taker buy ratio
    df = df.with_columns(
        pl.Series("MtmMean", (df["close"] / (df["close"].shift(n) + config.eps) - 1).ewm_mean(span=n, adjust=config.ewm_adjust))
    )
    df = df.with_columns(pl.Series("vma", df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("taker_buy_ma", (df["taker_buy_quote_asset_volume"] / (df["vma"] + config.eps)) * 100))
    df = df.with_columns(
        pl.Series("taker_buy_mean", df["taker_buy_ma"].rolling_mean(n, min_samples=config.min_periods))
    )

    df = df.with_columns(pl.Series(factor_name, df["MtmMean"] * df["taker_buy_mean"]))

    df = df.drop(["MtmMean", "vma", "taker_buy_ma", "taker_buy_mean"])

    return df
