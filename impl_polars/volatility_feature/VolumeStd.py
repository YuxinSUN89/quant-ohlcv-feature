import polars as pl


def signal(df, n, factor_name, config):
    # VolumeStd indicator (Rolling standard deviation of quote volume)
    # Formula: result = STD(QUOTE_VOLUME, N)
    # Measures the dispersion of quote volume over N periods. Higher values indicate
    # more erratic volume activity (spikes and lulls); lower values indicate steady volume.
    df = df.with_columns(
        pl.Series(factor_name, df["quote_volume"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof))
    )

    return df
