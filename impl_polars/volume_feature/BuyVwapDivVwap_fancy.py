import polars as pl


def signal(df, n, factor_name, config):
    # ratio of taker buy VWAP to current VWAP.
    df = df.with_columns(
        pl.Series(
            "vwap",
            df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
            / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
        )
    )
    if "taker_buy_base_asset_volume" in df.columns:
        df = df.with_columns(
            pl.Series(
                "buy_vwap",
                df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
                / df["taker_buy_base_asset_volume"].rolling_sum(n, min_samples=config.min_periods),
            )
        )
    else:
        df = df.with_columns(
            pl.Series(
                "buy_vwap",
                df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
                / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
            )
        )
    df = df.with_columns(pl.Series(factor_name, df["buy_vwap"] / df["vwap"]))

    df = df.drop(["vwap", "buy_vwap"])

    return df
