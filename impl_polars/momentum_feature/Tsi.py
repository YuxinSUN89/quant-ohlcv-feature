import polars as pl


def signal(df, n, factor_name, config):
    # TSI indicator
    """
    N1=25
    N2=13
    TSI=EMA(EMA(CLOSE-REF(CLOSE,1),N1),N2)/EMA(EMA(ABS(
    CLOSE-REF(CLOSE,1)),N1),N2)*100
    TSI is a double moving average indicator. Unlike the common moving average indicator which takes the moving average of the close price,
    TSI takes the moving average of the difference between two days' close prices. If TSI crosses above 10 /
    crosses below -10, it generates a buy/sell signal.
    """
    n1 = 2 * n
    df = df.with_columns(pl.Series("diff_close", df["close"] - df["close"].shift(1)))
    df = df.with_columns(pl.Series("ema", df["diff_close"].ewm_mean(span=n1, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema", df["ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series("abs_diff_close", abs(df["diff_close"])))
    df = df.with_columns(pl.Series("abs_ema", df["abs_diff_close"].ewm_mean(span=n1, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("abs_ema_ema", df["abs_ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series(factor_name, df["ema_ema"] / df["abs_ema_ema"] * 100))

    df = df.drop("diff_close")
    df = df.drop("ema")
    df = df.drop("ema_ema")
    df = df.drop("abs_diff_close")
    df = df.drop("abs_ema")
    df = df.drop("abs_ema_ema")

    return df
