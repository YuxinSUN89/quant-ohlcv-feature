import polars as pl


def signal(df, n, factor_name, config):
    # Mm indicator (Fast MA / Slow MA)
    # Formula: MA_FAST = MA(CLOSE, N); MA_SLOW = MA(CLOSE, 5N)
    #          result = MA_FAST / MA_SLOW - 1
    # Measures the relative divergence between a short and long moving average.
    # Positive values indicate short MA above long MA (uptrend); negative indicate downtrend.
    eps = config.eps
    ma_fast = df["close"].rolling_mean(n, min_samples=config.min_periods)
    ma_slow = df["close"].rolling_mean(5 * n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, ma_fast / (ma_slow + eps) - 1))

    return df
