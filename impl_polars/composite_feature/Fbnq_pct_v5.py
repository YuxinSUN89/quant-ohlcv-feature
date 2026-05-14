import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Fbnq_pct_v5 indicator (Fibonacci multi-period momentum × volatility composite)
    # Formula: FBNQ_MEAN = mean of EMA(CLOSE, pn) for pn in [5,8,13,21,34,55,89]; momentum = FBNQ_MEAN.pct_change(N)
    #          BBW = mean of STD(CLOSE,N)/MA(CLOSE,N) for pn in [5,8,13,21,34,55,89]
    #          result = momentum * BBW
    # Uses Fibonacci numbers as EMA periods to capture multi-scale trend momentum,
    # then multiplies by the average Bollinger bandwidth to scale momentum by market volatility.
    # Positive values indicate trending upward momentum with elevated volatility.
    params = [5, 8, 13, 21, 34, 55, 89]
    fbnq_sum = pl.Series(np.zeros(len(df)))
    bbw_sum = pl.Series(np.zeros(len(df)))
    for pn in params:
        # momentum
        fbnq_sum = fbnq_sum + df["close"].ewm_mean(span=pn, adjust=config.ewm_adjust)
        # volatility
        bbw_sum = bbw_sum + df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods) / df[
            "close"
        ].rolling_mean(n, min_samples=config.min_periods)
    # momentum
    fbnq_mean = fbnq_sum / len(params)
    fbnq_mean = fbnq_mean.pct_change(n)

    # volatility
    bbw_ori = bbw_sum / len(params)

    # momentum * volatility
    df = df.with_columns(pl.Series(factor_name, fbnq_mean * bbw_ori))

    return df
