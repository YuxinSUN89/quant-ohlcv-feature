def signal(df, n, factor_name, config):
    # Wc indicator
    eps = config.eps
    """
    WC=(HIGH+LOW+2*CLOSE)/4
    N1=20
    N2=40
    EMA1=EMA(WC,N1)
    EMA2=EMA(WC,N2)
    WC can also be used to replace the closing price in some technical indicators (though less common).
    Here we use the crossover of WC short-term and long-term moving averages to generate trading signals.
    """
    WC = (df["high"] + df["low"] + 2 * df["close"]) / 4  # WC=(HIGH+LOW+2*CLOSE)/4
    df["ema1"] = WC.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA1=EMA(WC,N1)
    df["ema2"] = WC.ewm(span=2 * n, adjust=config.ewm_adjust).mean()  # EMA2=EMA(WC,N2)
    # normalize
    df[factor_name] = df["ema1"] / (df["ema2"] + eps) - 1

    # remove redundant columns
    del df["ema1"], df["ema2"]

    return df
