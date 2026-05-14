import polars as pl


def signal(df, n, factor_name, config):
    # TakerByRatio indicator
    # Formula: result = SUM(taker_buy_quote_asset_volume, N) / SUM(quote_volume, N)
    # Measures the fraction of quote volume that was initiated by buyers (taker buys) over N periods.
    # Values close to 1 indicate strong buying pressure; values close to 0 indicate selling pressure.
    volume = df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
    buy_volume = df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, buy_volume / volume))

    return df
