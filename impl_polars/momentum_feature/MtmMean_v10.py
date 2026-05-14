import polars as pl


def signal(df, n, factor_name, config):
    # MtmMean_v10 indicator (MTM mean × combined volatility)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; VOLATILITY = MAX(HIGH,N)/MIN(LOW,N)-1 (N-period range)
    #          HOURLY_VOL = HIGH/LOW-1; result = MA(MTM,N) * (VOLATILITY + MA(HOURLY_VOL,N))
    # Amplifies the momentum mean by a combined volatility measure (long-range + average intrabar).
    # High values indicate strong directional momentum in a high-volatility environment.
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(
        pl.Series(
            "volatility",
            df["high"].rolling_max(n, min_samples=config.min_periods)
            / df["low"].rolling_min(n, min_samples=config.min_periods)
            - 1,
        )
    )
    df = df.with_columns(pl.Series("hourly_volatility", df["high"] / df["low"] - 1))
    df = df.with_columns(
        pl.Series("hourly_volatility_mean", df["hourly_volatility"].rolling_mean(n, min_samples=config.min_periods))
    )
    df = df.with_columns(
        pl.Series(
            factor_name,
            df["mtm"].rolling_mean(n, min_samples=config.min_periods)
            * (df["volatility"] + df["hourly_volatility_mean"]),
        )
    )

    df = df.drop(["mtm", "volatility", "hourly_volatility", "hourly_volatility_mean"])

    return df
