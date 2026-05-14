import polars as pl


def signal(df, n, factor_name, config):
    # Vma
    eps = config.eps
    """
    N=20
    PRICE=(HIGH+LOW+OPEN+CLOSE)/4
    VMA=MA(PRICE,N)
    VMA is simply a moving average that replaces the close price with the average of
    high, low, open and close. A buy/sell signal is generated when PRICE crosses above/below VMA.
    """
    price = (df["high"] + df["low"] + df["open"] + df["close"]) / 4  # PRICE=(HIGH+LOW+OPEN+CLOSE)/4
    vma = price.rolling_mean(n, min_samples=config.min_periods)  # VMA=MA(PRICE,N)
    df = df.with_columns(pl.Series(factor_name, price / (vma + eps) - 1))  # normalize

    return df
