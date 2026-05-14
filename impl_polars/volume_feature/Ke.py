import polars as pl


def signal(df, n, factor_name, config):
    # Ke indicator
    eps = config.eps
    # Formula: KE = SIGN(PRICE_CHANGE_N) * (VOLUME / VOLUME_MA_N) * PRICE_CHANGE_N^2
    # Ke is a momentum-volume composite factor. The sign of the n-period price change gives direction,
    # normalized volume amplifies the signal when volume is above average, and squaring the price
    # change emphasizes larger moves. Higher values indicate strong momentum backed by volume.
    volume_avg = df["volume"].rolling_mean(n, min_samples=config.min_periods)
    volume_stander = df["volume"] / volume_avg
    price_change = df["close"].pct_change(n)
    df = df.with_columns(
        pl.Series(factor_name, (price_change / (abs(price_change) + eps)) * volume_stander * price_change**2)
    )

    return df
