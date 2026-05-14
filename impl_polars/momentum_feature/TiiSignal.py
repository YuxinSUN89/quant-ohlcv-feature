import numpy as np
import polars as pl

from impl_polars.helpers import scale_zscore


def signal(df, n, factor_name, config):
    # ******************** TII ********************
    # N1=40
    # M=[N1/2]+1
    # N2=9
    # CLOSE_MA=MA(CLOSE,N1)
    # DEV=CLOSE-CLOSE_MA
    # DEVPOS=IF(DEV>0,DEV,0)
    # DEVNEG=IF(DEV<0,-DEV,0)
    # SUMPOS=SUM(DEVPOS,M)
    # SUMNEG=SUM(DEVNEG,M)
    # TII=100*SUMPOS/(SUMPOS+SUMNEG)
    # TII_SIGNAL=EMA(TII,N2)
    # TII is calculated the same way as RSI, but replaces the two-day price change with the difference between price and moving average.
    # TII can be used to reflect the price trend and trend strength. Generally, TII>80 (<20) indicates a strong uptrend (downtrend).
    # There are several ways to generate trading signals with TII: cross above 20 to buy, cross below 80 to sell (as a reversal indicator); cross above 50 to buy, cross below 50 to sell;
    # cross above signal line to buy, cross below signal line to sell. If TII crosses above TII_SIGNAL, a buy signal is generated; if TII crosses below TII_SIGNAL, a sell signal is generated.
    close_ma = df["close"].rolling_mean(n, min_samples=config.min_periods)
    dev = df["close"] - close_ma
    devpos = np.where(dev > 0, dev, 0)
    devpos = pl.Series(devpos).fill_nan(None)
    devneg = np.where(dev < 0, -dev, 0)
    devneg = pl.Series(devneg).fill_nan(None)
    sumpos = pl.Series(devpos).rolling_sum(int(1 + n / 2), min_samples=config.min_periods)
    sumneg = pl.Series(devneg).rolling_sum(int(1 + n / 2), min_samples=config.min_periods)

    tii = 100 * sumpos / (sumpos + sumneg)
    tii_signal = pl.Series(tii).ewm_mean(span=int(n / 2), adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series(factor_name, scale_zscore(tii_signal, n, config=config)))

    return df
