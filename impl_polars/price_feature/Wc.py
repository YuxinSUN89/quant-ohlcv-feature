import polars as pl


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
    df = df.with_columns(pl.Series("ema1", WC.ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema2", WC.ewm_mean(span=2 * n, adjust=config.ewm_adjust)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["ema1"] / (df["ema2"] + eps) - 1))

    # remove redundant columns
    df = df.drop(["ema1", "ema2"])

    return df
