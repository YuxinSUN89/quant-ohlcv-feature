import polars as pl


def signal(df, n, factor_name, config):
    # Average trade size per transaction, checking if large orders appeared in this minute
    if "trade_num" in df.columns:
        df = df.with_columns(
            pl.Series(
                factor_name,
                df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
                / df["trade_num"].rolling_sum(n, min_samples=config.min_periods),
            )
        )
    else:
        df = df.with_columns(pl.Series(factor_name, [None] * len(df)))

    return df
