import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    """
    Liquidity factor, derived from the stock selection strategy in the 2023 sharing session live broadcast episode 01;
    quote_volume / |price change|, i.e., how much trading volume is needed for price to move (up or down) 1 unit;
    smaller factor value means worse liquidity — less capital required per unit of fluctuation;
    """
    # Price path 1: open -> high -> low -> close
    df = df.with_columns(
        pl.Series("path_first", (df["high"] - df["open"]) + (df["high"] - df["low"]) + (df["close"] - df["low"]))
    )
    # Price path 2: open -> low -> high -> close
    df = df.with_columns(
        pl.Series("path_second", (df["open"] - df["low"]) + (df["high"] - df["low"]) + (df["high"] - df["close"]))
    )

    df = df.with_columns(path_min=pl.min_horizontal([pl.col("path_first"), pl.col("path_second")]))
    df = df.with_columns(
        pl.Series("change", df["high"] - df["low"])
    )  # if shortest path is 0, use this price spread instead
    df = df.with_columns(
        pl.Series("path_min", np.where(df["path_min"] == 0, df["change"], df["path_min"])).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("path_min", df["path_min"] + abs(df["open"] - df["close"].shift(1)))
    )  # gap up (or down) open

    # normalize shortest path
    df = df.with_columns(pl.Series("path_shortest", df["path_min"] / df["close"]))

    df = df.with_columns(
        pl.Series(
            "liq_raw", np.where(df["path_shortest"].fill_null(0) == 0, 0, df["quote_volume"] / df["path_shortest"])
        ).fill_nan(None)
    )
    # Fill remaining NaN in liq_raw (from null path_shortest at row 0) to match pandas NaN-skipping rolling_sum
    df = df.with_columns(pl.col("liq_raw").fill_null(0).alias("liq_raw"))
    df = df.with_columns(pl.Series(factor_name, df["liq_raw"].rolling_sum(n, min_samples=1)))  # or rolling_mean

    df = df.drop(["path_first", "path_second", "path_min", "change", "path_shortest", "liq_raw"])

    return df
