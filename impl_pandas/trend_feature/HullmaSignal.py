import numpy as np

from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Hullma indicator
    """
    N=20,80
    X=2*EMA(CLOSE,[N/2])-EMA(CLOSE,N)
    Hullma=EMA(X,[√N])
    Hullma is a type of moving average with lower lag compared to ordinary moving averages. We use
    the short-term moving average crossing above/below the long-term moving average to generate buy/sell signals.
    """
    _x = (
        2 * df["close"].ewm(span=int(n / 2), adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
        - df["close"].ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    )
    hullma = _x.ewm(span=int(np.sqrt(n)), adjust=config.ewm_adjust, min_periods=config.min_periods).mean()

    s = _x - hullma
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
