import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Reg indicator (Close vs linear regression)
    # Formula: REG = LINEARREG(CLOSE, N); result = CLOSE / REG - 1
    # Measures the deviation of close from its N-period linear regression value.
    # Positive values indicate close is above the regression line (overextended upward); negative below.
    df = df.with_columns(pl.Series("reg_close", ta.LINEARREG(df["close"], timeperiod=n)))
    df = df.with_columns(pl.Series(factor_name, df["close"] / df["reg_close"] - 1))

    # remove redundant columns
    df = df.drop("reg_close")

    return df
