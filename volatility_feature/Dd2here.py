def signal(df, n, factor_name, config):
    """
    Dd2here aims to construct a breakout-drawdown system, blacklisting for n hours when maximum drawdown exceeds a threshold
    """
    df["max2here"] = df["high"].rolling(n, min_periods=config.min_periods).max()
    df["dd1here"] = abs(df["close"] / df["max2here"] - 1)
    # df['avg_max_drawdown'] = df['dd1here'].rolling(n, min_periods=config.min_periods).mean()

    df["min2here"] = df["low"].rolling(n, min_periods=config.min_periods).min()
    df["dd2here"] = abs(df["close"] / df["min2here"] - 1)
    # df['avg_reverse_drawdown'] = df['dd2here'].rolling(n, min_periods=config.min_periods).mean()

    df[factor_name] = df[["dd1here", "dd2here"]].min(axis=1).rolling(n, min_periods=config.min_periods).max()
    drop_col = ["max2here", "dd1here", "min2here", "dd2here"]
    df.drop(columns=drop_col, inplace=True)

    return df
