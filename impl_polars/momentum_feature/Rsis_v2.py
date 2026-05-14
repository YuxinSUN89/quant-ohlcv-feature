import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # RSIS indicator
    """
    N=120
    M=20
    CLOSE_DIFF_POS=IF(CLOSE>REF(CLOSE,1),CLOSE-REF(CL
    OSE,1),0)
    RSI=SMA(CLOSE_DIFF_POS,N,1)/SMA(ABS(CLOSE-REF(CLOS
    E,1)),N,1)*100
    RSIS=(RSI-MIN(RSI,N))/(MAX(RSI,N)-MIN(RSI,N))*100
    RSISMA=EMA(RSIS,M)
    RSIS reflects where the current RSI falls between the maximum and minimum RSI values
    over the past N days, similar in concept to the KDJ indicator. Since RSIS is relatively
    volatile, we take a moving average first before generating signals. Usage is similar to RSI.
    A buy signal is generated when RSISMA crosses above 40;
    a sell signal is generated when RSISMA crosses below 60.
    """
    close_diff_pos = np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0)
    close_diff_pos = pl.Series(close_diff_pos).fill_nan(None)
    rsi_a = pl.Series(close_diff_pos).ewm_mean(alpha=1 / (4 * n), adjust=config.ewm_adjust)
    rsi_b = (df["close"] - df["close"].shift(1)).abs().ewm_mean(alpha=1 / (4 * n), adjust=config.ewm_adjust)
    rsi = 100 * rsi_a / (config.normalize_eps + rsi_b)
    rsi_min = pl.Series(rsi).rolling_min(int(4 * n), min_samples=config.min_periods)
    rsi_max = pl.Series(rsi).rolling_max(int(4 * n), min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, 100 * (rsi - rsi_min) / (config.normalize_eps + rsi_max - rsi_min)))

    return df
