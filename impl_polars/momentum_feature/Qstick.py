import numpy as np
import polars as pl


def _rolling_mean_np(values, window, min_periods):
    arr = np.asarray(values, dtype=float)
    out = np.full(len(arr), np.nan)
    min_p = min_periods or 1
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        w = arr[start : i + 1]
        valid = w[~np.isnan(w)]
        if len(valid) < min_p:
            continue
        out[i] = valid.mean()
    return out


def signal(df, n, factor_name, config):
    # Qstick indicator
    """
    N=20
    Qstick=MA(CLOSE-OPEN,N)
    Qstick reflects the direction and strength of price trends by comparing closing and opening prices.
    Buy/sell signals are generated when Qstick crosses above/below 0.
    """
    cl = df["close"] - df["open"]
    # Numerical sensitivity note:
    # Qstick can explode when the rolling mean of (close-open) is extremely close to zero.
    # pandas and polars sometimes disagree only because one side keeps a tiny signed residual
    # while the other collapses to exact 0.0, so we use a numpy rolling mean to stay as close
    # as possible to pandas behaviour near zero-denominator windows.
    qstick = pl.Series(_rolling_mean_np(cl.to_numpy(), n, config.min_periods))
    df = df.with_columns(pl.Series(factor_name, cl / qstick - 1))

    return df
