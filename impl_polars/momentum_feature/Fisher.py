import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # FISHER indicator
    """
    N=20
    PARAM=0.3
    PRICE=(HIGH+LOW)/2
    PRICE_CH=2*(PRICE-MIN(LOW,N)/(MAX(HIGH,N)-MIN(LOW,N))-0.5)
    PRICE_CHANGE=0.999 IF PRICE_CHANGE>0.99
    PRICE_CHANGE=-0.999 IF PRICE_CHANGE<-0.99
    PRICE_CHANGE=PARAM*PRICE_CH+(1-PARAM)*REF(PRICE_CHANGE,1)
    FISHER=0.5*REF(FISHER,1)+0.5*log((1+PRICE_CHANGE)/(1-PRICE_CHANGE))
    PRICE_CH measures the current price position between the highest and lowest prices over the past N periods.
    Fisher Transformation is a method that transforms stock price data to approximate a normal distribution.
    The advantage of the Fisher indicator is that it reduces the lag compared to common technical indicators.
    """
    PARAM = 1 / n
    df = df.with_columns(pl.Series("price", (df["high"] + df["low"]) / 2))
    df = df.with_columns(pl.Series("min_low", df["low"].rolling_min(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("max_high", df["high"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("price_ch", 2 * (df["price"] - df["min_low"]) / (df["max_high"] - df["min_low"] + config.eps) - 0.5))
    df = df.with_columns(pl.Series("price_change", PARAM * df["price_ch"] + (1 - PARAM) * df["price_ch"].shift(1)))
    df = df.with_columns(
        pl.Series("price_change", np.where(df["price_change"] > 0.99, 0.999, df["price_change"])).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("price_change", np.where(df["price_change"] < -0.99, -0.999, df["price_change"])).fill_nan(None)
    )
    df = df.with_columns(pl.Series(factor_name, 0.5 * np.log((1 + df["price_change"]) / (1 - df["price_change"]))))

    df = df.drop("price")
    df = df.drop("min_low")
    df = df.drop("max_high")
    df = df.drop("price_ch")
    df = df.drop("price_change")

    return df
