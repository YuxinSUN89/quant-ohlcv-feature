import numpy as np


def signal(df, n, factor_name, config):
    # HULLMA indicator
    """
    N=20,80
    X=2*EMA(CLOSE,[N/2])-EMA(CLOSE,N)
    HULLMA=EMA(X,[√N])
    HULLMA is a type of moving average with lower lag compared to ordinary moving averages. We use
    the short-term moving average crossing above/below the long-term moving average to generate buy/sell signals.
    """
    ema1 = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    ema2 = df["close"].ewm(span=n * 2, adjust=config.ewm_adjust).mean()
    df["X"] = 2 * ema1 - ema2
    df["HULLMA"] = df["X"].ewm(span=int(np.sqrt(2 * n)), adjust=config.ewm_adjust).mean()

    df[factor_name] = df["X"] / df["HULLMA"]

    del df["X"]
    del df["HULLMA"]

    return df
