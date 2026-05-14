import polars as pl


def signal(df, n, factor_name, config):
    # MtmMean_v12 indicator (MTM × normalized taker buy volume, rolling mean)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1
    #          MTM_ADJ = MTM * (taker_buy / MA(taker_buy, N))
    #          result = MA(MTM_ADJ, N)
    # Weights momentum by the ratio of taker buy volume to its rolling mean.
    # Above-average taker buying amplifies positive momentum; below-average dampens it.
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(
        pl.Series(
            "mtm",
            df["mtm"]
            * df["taker_buy_quote_asset_volume"]
            / df["taker_buy_quote_asset_volume"].rolling_mean(n, min_samples=config.min_periods),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    return df
