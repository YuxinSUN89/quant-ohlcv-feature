def signal(df, n, factor_name, config):
    # LMA indicator
    """
    N=20
    LMA=MA(LOW,N)
    LMA is a simple moving average with the closing price replaced by the lowest price.
    Buy/sell signals are generated when the low crosses above/below LMA.
    """
    df["low_ma"] = df["low"].rolling(n, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = df["low"] / df["low_ma"] - 1

    del df["low_ma"]

    return df
