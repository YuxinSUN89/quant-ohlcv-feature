def signal(df, n, factor_name, config):
    # RetBoll_fancy indicator (Bollinger Bands applied to returns / z-score of returns)
    # Formula: RTN = CLOSE.pct_change(); result = (RTN - MA(RTN,N)) / STD(RTN,N)
    # Applies z-score normalization to the return series rather than the price series.
    # Measures how extreme the current return is relative to recent return history.
    # High positive values indicate unusually strong up moves; high negative values indicate down moves.
    df["_ret"] = df["close"].pct_change()
    df[factor_name] = (df["_ret"] - df["_ret"].rolling(n, min_periods=config.min_periods).mean()) / df["_ret"].rolling(
        n, min_periods=config.min_periods
    ).std(ddof=config.ddof)

    del df["_ret"]

    return df
