def signal(df, n, factor_name, config):
    # Average trade size per transaction, checking if large orders appeared in this minute
    df[factor_name] = (
        df["quote_volume"].rolling(n, min_periods=config.min_periods).sum()
        / df["trade_num"].rolling(n, min_periods=config.min_periods).sum()
    )

    return df
