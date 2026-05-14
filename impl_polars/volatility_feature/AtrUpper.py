import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # AtrUpper indicator (ATR-based upper band ratio vs MA)
    # Formula: ATR = EMA(TR, N).shift(1); LOWER_N2 = MIN(LOW, N/2)
    #          result = (LOWER_N2 + 3 * ATR) / MA(CLOSE, N)
    # Constructs an ATR-based upper channel using recent low plus 3×ATR, normalized by the MA.
    # Values above 1 indicate the upper band is significantly above the MA (wide channel / high volatility).
    eps = config.eps
    tr = np.max(
        np.array(
            [
                (df["high"] - df["low"]).abs(),
                (df["high"] - df["close"].shift(1)).abs(),
                (df["low"] - df["close"].shift(1)).abs(),
            ]
        ),
        axis=0,
    )  # take the maximum of the three series
    atr = pl.Series(tr).ewm_mean(alpha=1 / n, adjust=config.ewm_adjust).shift(1)
    _low = df["low"].rolling_min(int(n / 2), min_samples=config.min_periods)
    _ma = df["close"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, (_low + 3 * atr) / (_ma + eps)))

    return df
