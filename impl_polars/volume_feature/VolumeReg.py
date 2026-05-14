import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # VolumeReg indicator (Linear Regression of Quote Volume)
    # Formula: result = LINEARREG(QUOTE_VOLUME, N)
    # Fits a linear regression to quote volume over N periods and returns the regression value.
    # Captures the trend direction and level of trading volume, smoothing out short-term noise.
    # Rising values indicate volume is trending up; falling values indicate declining volume trend.
    df = df.with_columns(pl.Series(factor_name, ta.LINEARREG(df["quote_volume"], timeperiod=n)))

    return df
