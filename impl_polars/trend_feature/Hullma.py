import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # HULLMA indicator
    """
    N=20,80
    X=2*EMA(CLOSE,[N/2])-EMA(CLOSE,N)
    HULLMA=EMA(X,[√N])
    HULLMA is a type of moving average with lower lag compared to ordinary moving averages. We use
    the short-term moving average crossing above/below the long-term moving average to generate buy/sell signals.
    """
    ema1 = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    ema2 = df["close"].ewm_mean(span=n * 2, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series("X", 2 * ema1 - ema2))
    df = df.with_columns(pl.Series("HULLMA", df["X"].ewm_mean(span=int(np.sqrt(2 * n)), adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series(factor_name, df["X"] / df["HULLMA"]))

    df = df.drop("X")
    df = df.drop("HULLMA")

    return df
