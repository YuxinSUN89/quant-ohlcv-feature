import polars as pl


def signal(df, n, factor_name, config):
    # Damaov10 indicator (COPP × BBW × ATR composite)
    # Formula: COPP = MA(100*((CLOSE-REF(CLOSE,N))/REF(CLOSE,N) + (CLOSE-REF(CLOSE,2N))/REF(CLOSE,2N)), N)
    #          BBW = STD * MA(|CLOSE-MA|/STD, N) * 2 / MA(CLOSE,N)  (volatility-weighted Bollinger width)
    #          ATR = MA(TR,N) / MA(CLOSE,N)  (normalized ATR)
    #          result = COPP * BBW_mean * ATR
    # Combines momentum (COPP), Bollinger volatility (BBW), and range volatility (ATR) into one composite signal.
    eps = config.eps
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
    # BBW
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("z_score", (df["close"] - df["median"]).abs() / (df["std"] + config.eps)))
    df = df.with_columns(pl.Series("m", df["z_score"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("BBW", df["std"] * df["m"] * 2 / (df["median"] + eps)))
    df = df.with_columns(pl.Series("BBW_mean", df["BBW"].rolling_mean(n, min_samples=config.min_periods)))
    # ATR
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("c2", (df["high"] - df["close"].shift(1)).abs()))
    df = df.with_columns(pl.Series("c3", (df["low"] - df["close"].shift(1)).abs()))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("_ATR", df["TR"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize ATR indicator
    df = df.with_columns(pl.Series("ATR", df["_ATR"] / (df["median"] + config.eps)))

    df = df.with_columns(pl.Series(factor_name, df["RC_mean"] * df["BBW_mean"] * df["ATR"]))
    # delete extra columns
    df = df.drop(["RC", "RC_mean", "median"])
    df = df.drop(["std", "z_score", "m"])
    df = df.drop(["BBW", "BBW_mean", "c1"])
    df = df.drop(["c2", "c3", "TR", "_ATR"])
    df = df.drop("ATR")

    return df
