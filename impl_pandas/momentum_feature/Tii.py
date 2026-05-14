import numpy as np
import pandas as pd

from impl_pandas.helpers import scale_01


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
    # TII is calculated like RSI, but the price change between two consecutive days is replaced
    # with the deviation of price from its moving average. TII reflects price trend direction and strength.
    # Generally, TII > 80 indicates a strong uptrend, TII < 20 indicates a strong downtrend.
    # Several methods can be used to generate signals: cross above 20 to buy, cross below 80 to sell (reversal);
    # cross above 50 to buy, cross below 50 to sell; or cross above signal line to buy, cross below to sell.
    # A buy signal is generated when TII crosses above TII_SIGNAL; a sell signal when TII crosses below TII_SIGNAL.
    close_ma = df["close"].rolling(n, min_periods=config.min_periods).mean()
    dev = df["close"] - close_ma
    devpos = np.where(dev > 0, dev, 0)
    devneg = np.where(dev < 0, -dev, 0)
    sumpos = pd.Series(devpos).rolling(int(1 + n / 2), min_periods=config.min_periods).sum()
    sumneg = pd.Series(devneg).rolling(int(1 + n / 2), min_periods=config.min_periods).sum()

    tii = 100 * sumpos / (sumpos + sumneg)
    df[factor_name] = scale_01(tii, n, config.normalize_eps, config=config)

    return df
