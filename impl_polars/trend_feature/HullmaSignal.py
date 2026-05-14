import numpy as np
import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Hullma indicator
    """
    N=20,80
    X=2*EMA(CLOSE,[N/2])-EMA(CLOSE,N)
    Hullma=EMA(X,[√N])
    Hullma is a type of moving average with lower lag compared to ordinary moving averages. We use
    the short-term moving average crossing above/below the long-term moving average to generate buy/sell signals.
    """
    _x = 2 * df["close"].ewm_mean(span=int(n / 2), adjust=config.ewm_adjust) - df["close"].ewm_mean(
        span=n, adjust=config.ewm_adjust
    )
    hullma = _x.ewm_mean(span=int(np.sqrt(n)), adjust=config.ewm_adjust)

    s = _x - hullma
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
