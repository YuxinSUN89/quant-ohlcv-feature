import polars as pl


def signal(df, n, factor_name, config):
    # TakerByRatioPerTrade indicator
    # Formula: TAKER_RATIO = SUM(taker_buy_quote,N) / SUM(quote_volume,N)
    #          result = TAKER_RATIO / MA(trade_num, N)
    # Normalizes the taker buy ratio by average number of trades per period.
    volume = df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
    buy_volume = df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)

    if "trade_num" in df.columns:
        df = df.with_columns(pl.Series("trade_mean", df["trade_num"].rolling_mean(n, min_samples=config.min_periods)))
        df = df.with_columns(pl.Series(factor_name, buy_volume / volume / df["trade_mean"]))
        df = df.drop("trade_mean")
    else:
        df = df.with_columns(pl.Series(factor_name, buy_volume / volume))

    return df
