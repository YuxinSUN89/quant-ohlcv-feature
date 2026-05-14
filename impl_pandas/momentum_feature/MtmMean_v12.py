def signal(df, n, factor_name, config):
    # MtmMean_v12 indicator (MTM × normalized taker buy volume, rolling mean)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1
    #          MTM_ADJ = MTM * (taker_buy / MA(taker_buy, N))
    #          result = MA(MTM_ADJ, N)
    # Weights momentum by the ratio of taker buy volume to its rolling mean.
    # Above-average taker buying amplifies positive momentum; below-average dampens it.
    df["mtm"] = df["close"] / (df["close"].shift(n) + config.eps) - 1
    df["mtm"] = (
        df["mtm"]
        * df["taker_buy_quote_asset_volume"]
        / df["taker_buy_quote_asset_volume"].rolling(window=n, min_periods=config.min_periods).mean()
    )
    df[factor_name] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean()

    return df
