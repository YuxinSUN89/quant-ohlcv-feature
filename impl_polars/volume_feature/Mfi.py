import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Note: n should not exceed half the number of filtered K-lines when using this indicator (not half the K-line data fetched)
    """
    N=14
    TYPICAL_PRICE=(HIGH+LOW+CLOSE)/3
    MF=TYPICAL_PRICE*VOLUME
    MF_POS=SUM(IF(TYPICAL_PRICE>=REF(TYPICAL_PRICE,1),MF,0),N)
    MF_NEG=SUM(IF(TYPICAL_PRICE<=REF(TYPICAL_PRICE,1),MF,0),N)
    MFI=100-100/(1+MF_POS/MF_NEG)
    The MFI indicator is calculated similarly to RSI, but differs in that the condition
    for up/down uses the typical price rather than the close price, and it sums MF rather than
    the change in close price. MFI can also be used to assess overbought and oversold market conditions.
    If MFI crosses above 80, a buy signal is generated;
    if MFI crosses below 20, a sell signal is generated.
    """
    # Numerical sensitivity note:
    # MFI gates money flow by comparing typical price to its one-step lag. Tiny CSV / float
    # differences around equality can change whether a row enters MF_POS or MF_NEG, so we round
    # the typical price to stabilize pandas/polars comparison behaviour.
    df = df.with_columns(pl.Series("price", ((df["high"] + df["low"] + df["close"]) / 3).round(12)))
    df = df.with_columns(pl.Series("MF", df["price"] * df["volume"]))
    df = df.with_columns(pl.Series("pos", np.where(df["price"] >= df["price"].shift(1), df["MF"], 0)).fill_nan(0))
    df = df.with_columns(pl.Series("MF_POS", df["pos"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("neg", np.where(df["price"] <= df["price"].shift(1), df["MF"], 0)).fill_nan(0))
    df = df.with_columns(pl.Series("MF_NEG", df["neg"].rolling_sum(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series(factor_name, 100 - 100 / (1 + df["MF_POS"] / df["MF_NEG"])))

    # delete intermediate data
    df = df.drop(["price", "MF", "pos", "MF_POS", "neg", "MF_NEG"])

    return df
