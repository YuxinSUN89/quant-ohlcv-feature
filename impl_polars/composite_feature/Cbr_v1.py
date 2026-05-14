import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Cbr_v1 indicator (COPP × BBW × price-volume correlation composite)
    # Formula: RC = 100 * (CLOSE_CHANGE_N/CLOSE_N + CLOSE_CHANGE_2N/CLOSE_2N); COPP = MA(RC, N)
    #          BBW = STD(CLOSE,N) / MA(CLOSE,N); CORR = CORREL(CLOSE, VOLUME, N) + 1
    #          CBR = COPP * BBW * MA(CORR, N)
    # Combines the Coppock curve (dual-window momentum) with Bollinger bandwidth (volatility)
    # and close-volume correlation. Higher values suggest trending momentum with high volatility
    # and price-volume alignment.

    # Copp
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
    df = df.with_columns(pl.Series("RC", df["RC"].rolling_mean(n, min_samples=config.min_periods)))

    # bbw
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("bbw", (df["std"] / (df["median"] + config.eps))))

    # corr
    df = df.with_columns(pl.Series("corr", ta.CORREL(df["close"], df["volume"], n) + 1))
    df = df.with_columns(pl.Series("corr", df["corr"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series(factor_name, df["RC"] * df["bbw"] * df["corr"]))

    df = df.drop(["RC", "median", "std", "bbw", "corr"])

    return df
