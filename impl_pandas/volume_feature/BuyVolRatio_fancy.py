def signal(df, n, factor_name, config):
    # taker buy ratio over the past N periods
    df[factor_name] = (
        df["taker_buy_quote_asset_volume"].rolling(n, min_periods=config.min_periods).sum()
        / (df["quote_volume"].rolling(n, min_periods=config.min_periods).sum() + config.eps)
    )

    return df
