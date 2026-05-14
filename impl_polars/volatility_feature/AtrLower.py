import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # AtrLower indicator (ATR lower band ratio vs MA)
    # Formula: ATR = MA(TR, N); MA = MA(CLOSE, N)
    #          LOWER = MA - ATR * 0.2 * N; result = LOWER / MA
    # Computes an ATR-based lower band scaled by window length, normalized as a ratio to MA.
    # Values below 1 indicate the lower band is significantly below the moving average (wide channel).
    eps = config.eps
    tr = np.max(
        np.array(
            [
                df["high"] - df["low"],
                (df["high"] - df["close"].shift(1)).abs(),
                (df["low"] - df["close"].shift(1)).abs(),
            ]
        ),
        axis=0,
    )
    atr = pl.Series(tr).rolling_mean(n, min_samples=config.min_periods)
    _ma = df["close"].rolling_mean(n, min_samples=config.min_periods)

    dn = _ma - atr * 0.2 * n
    df = df.with_columns(pl.Series(factor_name, dn / (_ma + eps)))

    return df
