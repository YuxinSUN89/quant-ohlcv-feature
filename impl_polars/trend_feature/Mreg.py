import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Mreg indicator (Rolling mean of close vs linear regression residual)
    # Formula: REG = LINEARREG(CLOSE, N); MREG = CLOSE/REG - 1; result = MA(MREG, N)
    # Measures how much close deviates from its linear regression trend, then smooths with rolling mean.
    # Captures sustained over/under-performance relative to the trend line.
    df = df.with_columns(pl.Series("reg_close", ta.LINEARREG(df["close"], timeperiod=n)))
    df = df.with_columns(pl.Series("mreg", df["close"] / df["reg_close"] - 1))
    # fill_nan(None) converts float NaN (from talib head) to polars null so rolling_mean skips them,
    # matching pandas rolling().mean() NaN-skipping behaviour.
    df = df.with_columns(pl.col("mreg").fill_nan(None).alias("mreg"))
    df = df.with_columns(pl.Series(factor_name, df["mreg"].rolling_mean(n, min_samples=config.min_periods)))

    # remove redundant columns
    df = df.drop(["reg_close", "mreg"])

    return df
