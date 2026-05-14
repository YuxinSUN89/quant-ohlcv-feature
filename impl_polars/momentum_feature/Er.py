import polars as pl


def signal(df, n, factor_name, config):
    # Er indicator
    """
    N=20
    BullPower=HIGH-EMA(CLOSE,N)
    BearPower=LOW-EMA(CLOSE,N)
    ER is a momentum indicator used to measure the bull/bear power balance in the market.
    In a bull market, people buy more greedily near the high price; the higher the BullPower, the stronger the current bull force.
    In a bear market, people may sell out of fear near the low price; the lower the BearPower, the stronger the current bear force.
    When both are greater than 0, it reflects that bulls currently dominate;
    when both are less than 0, it reflects that bears dominate.
    If BearPower crosses above 0, a buy signal is generated;
    if BullPower crosses below 0, a sell signal is generated.
    """

    df = df.with_columns(pl.Series("ema", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("BullPower", (df["high"] - df["ema"]) / df["ema"]))
    df = df.with_columns(pl.Series("BearPower", (df["low"] - df["ema"]) / df["ema"]))
    df = df.with_columns(pl.Series(factor_name, df["BullPower"] + df["BearPower"]))

    # delete extra columns
    df = df.drop(["ema", "BullPower", "BearPower"])

    return df
