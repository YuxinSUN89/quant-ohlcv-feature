import polars as pl


def signal(df, n, factor_name, config):
    # MtmBear indicator (MTM mean × ATR × Taker sell composite)
    # Formula: MTM_MEAN = MA(CLOSE/REF(MA,N)-1, N) * 100; ATR = MA(TR,N)/MA * 100
    #          TAKER_SELL_MEAN = MA(taker_sell/MA(quote_volume)*100, N)
    #          result = MTM_MEAN * ATR * TAKER_SELL_MEAN
    # Bearish composite: momentum × volatility × seller-initiated volume.
    # Large positive values indicate strong downside momentum in a volatile, seller-dominated market.
    # momentum
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("mtm", (df["close"] / (df["ma"] + config.eps).shift(n) - 1) * 100))
    df = df.with_columns(pl.Series("mtm_mean", df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    # average amplitude
    df = df.with_columns(pl.Series("tr1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("tr2", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("tr3", abs(df["low"] - df["close"].shift(1))))
    df = df.with_columns(tr=pl.max_horizontal([pl.col("tr1"), pl.col("tr2"), pl.col("tr3")]))
    df = df.with_columns(pl.Series("ATR_abs", df["tr"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ATR", df["ATR_abs"] / (df["ma"] + config.eps) * 100))

    # average taker sell volume
    df = df.with_columns(
        pl.Series("taker_sell_quote_asset_volume", df["quote_volume"] - df["taker_buy_quote_asset_volume"])
    )
    df = df.with_columns(pl.Series("vma", df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("taker_sell_ma", (df["taker_sell_quote_asset_volume"] / (df["vma"] + config.eps)) * 100))
    df = df.with_columns(
        pl.Series("taker_sell_mean", df["taker_sell_ma"].rolling_mean(n, min_samples=config.min_periods))
    )

    # combined indicator
    df = df.with_columns(pl.Series(factor_name, df["mtm_mean"] * df["ATR"] * df["taker_sell_mean"]))

    drop_col = [
        "ma",
        "mtm",
        "mtm_mean",
        "tr1",
        "tr2",
        "tr3",
        "tr",
        "ATR_abs",
        "ATR",
        "taker_sell_quote_asset_volume",
        "vma",
        "taker_sell_ma",
        "taker_sell_mean",
    ]
    df = df.drop(drop_col)

    return df
