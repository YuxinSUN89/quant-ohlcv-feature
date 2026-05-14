def signal(df, n, factor_name, config):
    # TradeNum indicator
    # Formula: result = SUM(trade_num, N)
    # Rolling sum of the number of trades over N periods. A proxy for market activity and liquidity.
    # Higher values indicate more transactions occurring, often associated with increased market interest.
    df[factor_name] = df["trade_num"].rolling(n, min_periods=config.min_periods).sum()

    return df
