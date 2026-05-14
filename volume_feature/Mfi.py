import numpy as np


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
    # differences around equality can change whether a row enters MF_POS or MF_NEG.
    df["price"] = (df["high"] + df["low"] + df["close"]) / 3  # TYPICAL_PRICE=(HIGH+LOW+CLOSE)/3
    df["MF"] = df["price"] * df["volume"]  # MF=TYPICAL_PRICE*VOLUME
    df["pos"] = np.where(
        df["price"] >= df["price"].shift(1), df["MF"], 0
    )  # IF(TYPICAL_PRICE>=REF(TYPICAL_PRICE,1),MF,0)MF,0),N)
    df["MF_POS"] = df["pos"].rolling(n, min_periods=config.min_periods).sum()
    df["neg"] = np.where(
        df["price"] <= df["price"].shift(1), df["MF"], 0
    )  # IF(TYPICAL_PRICE<=REF(TYPICAL_PRICE,1),MF,0)
    df["MF_NEG"] = (
        df["neg"].rolling(n, min_periods=config.min_periods).sum()
    )  # MF_NEG=SUM(IF(TYPICAL_PRICE<=REF(TYPICAL_PRICE,1),MF,0),N)

    df[factor_name] = 100 - 100 / (1 + df["MF_POS"] / df["MF_NEG"])  # MFI=100-100/(1+MF_POS/MF_NEG)

    # delete intermediate data
    del df["price"]
    del df["MF"]
    del df["pos"]
    del df["MF_POS"]
    del df["neg"]
    del df["MF_NEG"]

    return df
