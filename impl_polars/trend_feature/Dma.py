import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Dma indicator (ATR-scaled MA difference)
    # Formula: ATR_X = ATR(N) / SUM(ATR,N); MA_SHORT = MA(CLOSE,N); MA_LONG = MA(CLOSE,2N)
    #          MA_DIF = MA_SHORT - MA_LONG; DMA = MA_DIF / SUM(|MA_DIF|,2N) + 1
    #          result = DMA * (1 + ATR_X)
    # Combines a normalized MA crossover signal with ATR volatility weighting.
    # Values above 1 suggest upward-trending regime; amplified further in high-volatility periods.
    atr = ta.ATR(df["high"], df["low"], df["close"], timeperiod=n)
    # Convert initial NaN from TA-Lib ATR to null so polars rolling_sum skips them like pandas rolling.sum().
    atr_sum = atr.fill_nan(None).rolling_sum(n, min_samples=1)
    atr_x = atr / atr_sum

    ma_short = df["close"].rolling_mean(n, min_samples=config.min_periods)
    ma_long = df["close"].rolling_mean(2 * n, min_samples=config.min_periods)
    ma_dif = ma_short - ma_long
    dma = (ma_dif / abs(ma_dif).rolling_sum(2 * n, min_samples=config.min_periods)) + 1
    df = df.with_columns(pl.Series(factor_name, dma * (1 + atr_x)))

    return df
