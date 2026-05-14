import polars as pl


def signal(df, n, factor_name, config):
    # Bias_v4 indicator (Typical price bias from MA)
    # Formula: TP = (HIGH + LOW + CLOSE) / 3; result = TP / MA(TP, N) - 1
    # Uses the typical price (HLC/3) instead of close to compute the bias from MA.
    # More representative of the full candle range than close-only bias.
    eps = config.eps
    ts = (df["high"] + df["low"] + df["close"]) / 3.0
    ma = ts.rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, ts / (ma + eps) - 1))

    return df
