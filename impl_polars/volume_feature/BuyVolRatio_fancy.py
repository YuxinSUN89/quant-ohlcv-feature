import polars as pl


def signal(df, n, factor_name, config):
    # taker buy ratio over the past N periods
    df = df.with_columns(
        pl.Series(
            factor_name,
            df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
            / df["quote_volume"].rolling_sum(n, min_samples=config.min_periods),
        )
    )

    return df
