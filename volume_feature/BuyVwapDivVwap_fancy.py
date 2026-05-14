def signal(df, n, factor_name, config):
    # ratio of taker buy VWAP to current VWAP.
    df["vwap"] = (
        df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
        / df["volume"].rolling(n, min_periods=config.min_periods).sum()
    )
    df["buy_vwap"] = (
        df["taker_buy_quote_asset_volume"].rolling(n, min_periods=config.min_periods).sum()
        / df["taker_buy_base_asset_volume"].rolling(n, min_periods=config.min_periods).sum()
    )
    df[factor_name] = df["buy_vwap"] / df["vwap"]

    del df["vwap"], df["buy_vwap"]

    return df
