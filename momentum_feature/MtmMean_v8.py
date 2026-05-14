def signal(df, n, factor_name, config):
    # Mtm multiplied by volatility, where volatility is expressed as the ratio of high to low
    df["mtm"] = df["close"] / df["close"].shift(n) - 1
    df["volatility"] = (
        df["high"].rolling(n, min_periods=config.min_periods).max()
        / df["low"].rolling(n, min_periods=config.min_periods).min()
        - 1
    )
    df[factor_name] = df["mtm"].rolling(window=n, min_periods=config.min_periods).mean() * df["volatility"]

    del df["mtm"], df["volatility"]

    return df
