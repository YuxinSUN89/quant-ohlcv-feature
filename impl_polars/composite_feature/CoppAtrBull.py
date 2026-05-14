import polars as pl


def signal(df, n, factor_name, config):
    # CoppAtrBull indicator (COPP × ATR × taker buy activity composite)
    # Formula: COPP = MA(100*((CLOSE-REF(CLOSE,N))/REF(CLOSE,N) + (CLOSE-REF(CLOSE,2N))/REF(CLOSE,2N)), N)
    #          ATR = MA(TR,N) / MA(CLOSE,N)  (normalized average true range)
    #          TAKER_BUY = MA(TAKER_BUY_QUOTE_VOLUME / MA(QUOTE_VOLUME,N) * 100, N)
    #          result = COPP * ATR * TAKER_BUY
    # Composite of Coppock momentum, volatility (ATR), and bullish taker buy pressure.
    # High positive values indicate momentum up with expanding volatility and strong buy activity.
    # COPP
    # RC=100*((CLOSE-REF(CLOSE,N1))/REF(CLOSE,N1)+(CLOSE-REF(CLOSE,N2))/REF(CLOSE,N2))
    df = df.with_columns(
        pl.Series(
            "RC",
            100
            * (
                (df["close"] - df["close"].shift(n)) / (df["close"].shift(n) + config.eps)
                + (df["close"] - df["close"].shift(2 * n)) / (df["close"].shift(2 * n) + config.eps)
            ),
        )
    )
    df = df.with_columns(pl.Series("RC_mean", df["RC"].rolling_mean(n, min_samples=config.min_periods)))

    # ATR
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", (df["high"] - df["close"].shift(1)).abs()))
    df = df.with_columns(pl.Series("c3", (df["low"] - df["close"].shift(1)).abs()))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("_ATR", df["TR"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize ATR indicator
    df = df.with_columns(pl.Series("ATR", df["_ATR"] / (df["median"] + config.eps)))

    # average taker buy ratio
    df = df.with_columns(pl.Series("vma", df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("taker_buy_ma", (df["taker_buy_quote_asset_volume"] / (df["vma"] + config.eps)) * 100))
    df = df.with_columns(
        pl.Series("taker_buy_mean", df["taker_buy_ma"].rolling_mean(n, min_samples=config.min_periods))
    )

    # composite indicator
    df = df.with_columns(pl.Series(factor_name, df["RC_mean"] * df["ATR"] * df["taker_buy_mean"]))
    # delete extra columns
    df = df.drop(["RC", "RC_mean"])
    df = df.drop(["median", "c1", "c2", "c3", "TR", "_ATR", "ATR"])
    df = df.drop(["vma", "taker_buy_ma", "taker_buy_mean"])

    return df
