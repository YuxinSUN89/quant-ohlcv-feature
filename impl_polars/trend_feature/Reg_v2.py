import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Reg_v2 indicator (Close vs longer-period linear regression, percentage)
    # Formula: REG = LINEARREG(CLOSE, 2N); result = 100 * (CLOSE - REG) / (REG + eps)
    # Measures the percentage deviation of close from its 2N-period linear regression value.
    # Uses a longer regression window (2N) than Reg.py for a smoother trend baseline.
    # Positive values indicate close is above the regression line; negative below.
    eps = config.eps
    df = df.with_columns(pl.Series("LINEARREG", ta.LINEARREG(df["close"], timeperiod=2 * n)))
    df = df.with_columns(pl.Series(factor_name, 100 * (df["close"] - df["LINEARREG"]) / (df["LINEARREG"] + eps)))

    # remove redundant columns
    df = df.drop("LINEARREG")

    return df
