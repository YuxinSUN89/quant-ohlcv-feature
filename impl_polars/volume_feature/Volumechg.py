import polars as pl


def signal(df, n, factor_name, config):
    # Volumechg indicator (Direction-weighted Volume Change rolling max)
    # Formula: DIRECTION = +1 if CLOSE > REF(CLOSE,1) else -1
    #          VOL_CHANGE = (QUOTE_VOLUME / REF(QUOTE_VOLUME,1)) * DIRECTION
    #          result = ROLLING_MAX(VOL_CHANGE, N)
    # Captures the maximum directional volume change over N periods. Positive values indicate
    # that large volume surges occurred on up-days; negative values indicate surges on down-days.
    df = df.with_columns(pl.Series("hourly_price_change", df["close"].pct_change(1)))
    df = df.with_columns(pl.Series("direction", [float("nan")] * len(df)))
    df = df.with_columns(
        pl.when(df["hourly_price_change"] > 0).then(1).otherwise(pl.col("direction")).alias("direction")
    )
    df = df.with_columns(
        pl.when(df["hourly_price_change"] < 0).then(-1).otherwise(pl.col("direction")).alias("direction")
    )
    df = df.with_columns(pl.Series("volume_change", df["quote_volume"] / (df["quote_volume"].shift(1) + config.eps) * df["direction"]))
    # fill_nan(None): direction=NaN (zero-change rows) and shift NaN propagate; convert to null so rolling_max skips them
    df = df.with_columns(
        pl.Series(factor_name, df["volume_change"].fill_nan(None).rolling_max(n, min_samples=config.min_periods))
    )

    return df
