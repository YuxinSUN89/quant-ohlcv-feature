import polars as pl


def signal(df, n, factor_name, config):
    """
    AdaptBollingv3
    Use the mtm_mean from the original v3 timing strategy as the factor B selector.
    """
    n1 = int(n)

    # ==============================================================

    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n1) + config.eps) - 1))
    df = df.with_columns(pl.Series("mtm_mean", df["mtm"].rolling_mean(n1, min_samples=config.min_periods)))

    # calculate volatility factor wd_atr based on price ATR
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"].shift(1))))
    df = df.with_columns(tr=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("atr", df["tr"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("avg_price_", df["close"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("wd_atr", df["atr"] / (df["avg_price_"] + config.eps)))

    # reference ATR to calculate volatility factor for MTM indicator
    df = df.with_columns(pl.Series("mtm_l", df["low"] / df["low"].shift(n1) - 1))
    df = df.with_columns(pl.Series("mtm_h", df["high"] / df["high"].shift(n1) - 1))
    df = df.with_columns(pl.Series("mtm_c", df["close"] / (df["close"].shift(n1) + config.eps) - 1))
    df = df.with_columns(pl.Series("mtm_c1", df["mtm_h"] - df["mtm_l"]))
    df = df.with_columns(pl.Series("mtm_c2", abs(df["mtm_h"] - df["mtm_c"].shift(1))))
    df = df.with_columns(pl.Series("mtm_c3", abs(df["mtm_l"] - df["mtm_c"].shift(1))))
    df = df.with_columns(mtm_tr=pl.max_horizontal([pl.col("mtm_c1"), pl.col("mtm_c2"), pl.col("mtm_c3")]))
    df = df.with_columns(pl.Series("mtm_atr", df["mtm_tr"].rolling_mean(n1, min_samples=config.min_periods)))

    # reference ATR to calculate volatility factor for MTM mean indicator
    df = df.with_columns(pl.Series("mtm_l_mean", df["mtm_l"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mtm_h_mean", df["mtm_h"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mtm_c_mean", df["mtm_c"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mtm_c1", df["mtm_h_mean"] - df["mtm_l_mean"]))
    df = df.with_columns(pl.Series("mtm_c2", abs(df["mtm_h_mean"] - df["mtm_c_mean"].shift(1))))
    df = df.with_columns(pl.Series("mtm_c3", abs(df["mtm_l_mean"] - df["mtm_c_mean"].shift(1))))
    df = df.with_columns(mtm_tr=pl.max_horizontal([pl.col("mtm_c1"), pl.col("mtm_c2"), pl.col("mtm_c3")]))
    df = df.with_columns(pl.Series("mtm_atr_mean", df["mtm_tr"].rolling_mean(n1, min_samples=config.min_periods)))

    indicator = "mtm_mean"

    # multiply mtm_mean indicator by three volatility factors
    df = df.with_columns(pl.Series(indicator, df[indicator] * df["mtm_atr"]))
    df = df.with_columns(pl.Series(indicator, df[indicator] * df["mtm_atr_mean"]))
    df = df.with_columns(pl.Series(indicator, df[indicator] * df["wd_atr"]))

    df = df.with_columns(pl.Series(factor_name, df[indicator] * 100000000))

    drop_col = [
        "mtm",
        "mtm_mean",
        "c1",
        "c2",
        "c3",
        "tr",
        "atr",
        "wd_atr",
        "mtm_l",
        "mtm_h",
        "mtm_c",
        "mtm_c1",
        "mtm_c2",
        "mtm_c3",
        "mtm_tr",
        "mtm_atr",
        "mtm_l_mean",
        "mtm_h_mean",
        "mtm_c_mean",
        "mtm_atr_mean",
        "avg_price_",
    ]
    df = df.drop(drop_col)

    return df
