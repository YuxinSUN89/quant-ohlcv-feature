import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Rwi indicator (Random Walk Index composite)
    # Formula: ATR = MA(TR, N)
    #          RWIH = (HIGH - REF(LOW,1)) / (SQRT(N) * ATR)   (upward RWI)
    #          RWIL = (REF(HIGH,1) - LOW) / (SQRT(N) * ATR)   (downward RWI)
    #          result = (CLOSE - RWIL) / (RWIH - RWIL)
    # The Random Walk Index measures whether price movement is beyond random (greater than 1 = trending).
    # This composite normalizes the close within the [RWIL, RWIH] range, giving a [0,1]-like score.
    tr = np.max(
        np.array(
            [
                (df["high"] - df["low"]).abs(),
                (df["high"] - df["close"].shift(1)).abs(),
                (df["close"].shift(1) - df["low"]).abs(),
            ]
        ),
        axis=0,
    )  # take the maximum of the three series

    atr = pl.Series(tr).rolling_mean(n, min_samples=config.min_periods)
    _rwih = (df["high"] - df["low"].shift(1)) / (np.sqrt(n) * atr)
    _rwil = (df["high"].shift(1) - df["low"]) / (np.sqrt(n) * atr)

    _rwi = (df["close"] - _rwil) / (config.normalize_eps + _rwih - _rwil)
    df = df.with_columns(pl.Series(factor_name, _rwi))

    return df
