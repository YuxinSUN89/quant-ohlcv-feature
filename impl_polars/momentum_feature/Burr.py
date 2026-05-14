import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Burr indicator (pullback depth in uptrends / rebound height in downtrends)
    # Formula (uptrend): SCORE_HIGH = 1 - CLOSE / MAX(HIGH,N)  where CLOSE > OPEN shifted by N
    #          (downtrend): SCORE_LOW = 1 - CLOSE / MIN(LOW,N)  where CLOSE < OPEN shifted by N
    #          result = SCORE_HIGH + SCORE_LOW (one will always be 0)
    # In uptrends, measures how far close has pulled back from the N-period high (deeper pullback → larger value).
    # In downtrends, measures the rebound height from the N-period low. Range: [-1, 1].
    # only observe pullback magnitude during uptrends
    scores_high = pl.Series(
        np.where(
            df["close"] - df["open"].shift(n) > 0,
            1 - df["close"] / df["high"].rolling_max(n, min_samples=config.min_periods),
            0,
        )
    )
    df = df.with_columns(pl.Series("scores_high", scores_high))
    # only observe rebound magnitude during downtrends
    scores_low = pl.Series(
        np.where(
            df["close"] - df["open"].shift(n) < 0,
            1 - df["close"] / df["low"].rolling_min(n, min_samples=config.min_periods),
            0,
        )
    )
    df = df.with_columns(pl.Series("scores_low", scores_low))
    df = df.with_columns(
        pl.Series(factor_name, df["scores_high"].fill_null(0) + df["scores_low"].fill_null(0))
    )  # [-1, 1]

    return df
