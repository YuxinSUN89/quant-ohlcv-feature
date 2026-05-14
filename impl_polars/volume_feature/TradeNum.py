import polars as pl


def signal(df, n, factor_name, config):
    # TradeNum indicator
    # Formula: result = SUM(trade_num, N)
    # Rolling sum of the number of trades over N periods.
    if "trade_num" in df.columns:
        df = df.with_columns(pl.Series(factor_name, df["trade_num"].rolling_sum(n, min_samples=config.min_periods)))
    else:
        df = df.with_columns(pl.Series(factor_name, [None] * len(df)))

    return df
