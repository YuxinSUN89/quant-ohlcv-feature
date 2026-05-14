import polars as pl


def signal(df, n, factor_name, config):
    # Ax10 indicator (TMA momentum × ATR volatility × taker buy composite)
    # Formula: TMA = MA(MA((HIGH+LOW)/2, N), N); MTM = CLOSE/(TMA+eps) - 1
    #          WD_ATR = ATR(N) / MA(CLOSE,N)  (normalized ATR)
    #          TAKER_BUY = MA(TAKER_BUY_QUOTE_VOLUME / MA(QUOTE_VOLUME,N) * 100, N)
    #          result = MA(MTM,N) * WD_ATR * TAKER_BUY * 1e8
    # Composite factor combining triangular MA momentum, ATR volatility, and taker buy pressure.
    # Scaled by 1e8 to amplify small values for practical use.
    eps = config.eps

    n1 = int(n)

    # ==============================================================
    ts = (df["high"] + df["low"]) / 2

    close_ma = ts.rolling_mean(n, min_samples=config.min_periods)
    tma = close_ma.rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("mtm", df["close"] / (tma + eps) - 1))

    df = df.with_columns(pl.Series("mtm_mean", df["mtm"].rolling_mean(n1, min_samples=config.min_periods)))

    # calculate volatility factor wd_atr based on price ATR
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["low"] - df["close"].shift(1))))
    df = df.with_columns(tr=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("atr", df["tr"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("avg_price_", df["close"].rolling_mean(n1, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("wd_atr", df["atr"] / (df["avg_price_"] + config.eps)))

    # average taker buy ratio
    df = df.with_columns(pl.Series("vma", df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("taker_buy_ma", (df["taker_buy_quote_asset_volume"] / (df["vma"] + config.eps)) * 100))
    df = df.with_columns(
        pl.Series("taker_buy_mean", df["taker_buy_ma"].rolling_mean(n, min_samples=config.min_periods))
    )

    indicator = "mtm_mean"

    # multiply mtm_mean indicator by three volatility factors
    df = df.with_columns(pl.Series(indicator, df[indicator] * df["wd_atr"] * df["taker_buy_mean"]))
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
        "avg_price_",
        "vma",
        "taker_buy_ma",
        "taker_buy_mean",
    ]
    df = df.drop(drop_col)

    return df
