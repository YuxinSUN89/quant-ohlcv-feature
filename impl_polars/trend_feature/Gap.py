import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # GAP indicator (WMA vs MA normalized gap)
    # Formula: MA = MA(CLOSE,N); WMA = WMA(CLOSE,N); GAP = WMA - MA
    #          result = GAP / SUM(|GAP|, N)
    # Measures the directional gap between weighted and simple moving averages, normalized by its own magnitude sum.
    # Positive values indicate WMA > MA (recent prices stronger than average, upward momentum); negative when reversed.
    df = df.with_columns(pl.Series("_ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("_wma", ta.WMA(df["close"], n)))
    df = df.with_columns(pl.Series("_gap", df["_wma"] - df["_ma"]))
    # Under the configured pandas proxy, rolling(window=n) inherits suite-level min_periods=1.
    # Convert initial NaN from WMA to null so polars rolling_sum skips them like pandas rolling.sum().
    gap_abs_sum = abs(df["_gap"]).fill_nan(None).rolling_sum(n, min_samples=1)
    df = df.with_columns(pl.Series(factor_name, (df["_gap"] / gap_abs_sum)))

    df = df.drop("_ma")
    df = df.drop("_wma")
    df = df.drop("_gap")

    return df
