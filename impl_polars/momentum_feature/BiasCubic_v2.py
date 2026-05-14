import polars as pl


def signal(df, n, factor_name, config):
    """
    BiasCubic indicator - product of three bias values
    Minimize variables: back_hour_list = [3, 4, 6, 8, 9, 12, 24, 30, 36, 48, 60, 72, 96]
    Taking int(n / 2), dividing by 1.5, and multiplying by 1.5 to create three distinctions is also viable - achieving three uses from one variable.
    :param args:
    :return:
    """
    df = df.with_columns(pl.Series("ma_1", df["close"].rolling_mean(int(n / 2), min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ma_2", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ma_3", df["close"].rolling_mean(n * 2, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("bias_1", (df["close"] / df["ma_1"] - 1)))
    df = df.with_columns(pl.Series("bias_2", (df["close"] / df["ma_2"] - 1)))
    df = df.with_columns(pl.Series("bias_3", (df["close"] / df["ma_3"] - 1)))

    df = df.with_columns(
        pl.Series(
            "mtm",
            (df["bias_1"] * df["bias_2"] * df["bias_3"])
            * df["quote_volume"]
            / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop(["ma_1", "ma_2", "ma_3", "bias_1", "bias_2", "bias_3", "mtm"])

    return df
