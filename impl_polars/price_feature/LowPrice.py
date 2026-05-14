import polars as pl


# LowPrice indicator (rolling mean close price — low-priced asset factor)
# Formula: result = MA(CLOSE, N)
# Returns the raw N-period moving average of close price as a factor.
# Used to identify low-priced assets; lower values indicate cheaper assets relative to history.
def signal(df, n, factor_name, config):
    df = df.with_columns(pl.Series(factor_name, df["close"].rolling_mean(n, min_samples=config.min_periods)))

    return df


from impl_polars.helpers import rolling_mean_multi


def signal_multi_params(df, param_list, config) -> dict:
    return rolling_mean_multi(df, param_list, "close", config)
