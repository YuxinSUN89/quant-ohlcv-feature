import polars as pl


def signal(df, n, factor_name, config):
    # Msbt indicator (Momentum × Std-Momentum × BBW × Taker Buy composite)
    # Formula: MTM = MA(CLOSE/REF(CLOSE,N)-1, N); S_MTM = MA(STD/REF(STD,N)-1, N)
    #          BBW = STD(CLOSE,N) / MA(CLOSE,N); TAKER_VOL = SUM(taker_buy,N) / SUM(taker_buy, 0.5N)
    #          MSBT = MTM * S_MTM * BBW_MEAN * TAKER_VOL
    # Combines price momentum, volatility momentum (std change), Bollinger bandwidth, and taker buy activity.
    # High values indicate accelerating price with expanding volatility and strong buying pressure.
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))

    # close price momentum
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("mtm", df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    # standard deviation momentum
    df = df.with_columns(pl.Series("s_mtm", df["std"] / (df["std"] + config.eps).shift(n) - 1))
    df = df.with_columns(pl.Series("s_mtm", df["s_mtm"].rolling_mean(n, min_samples=config.min_periods)))

    # bbw volatility
    df = df.with_columns(pl.Series("bbw", df["std"] / (df["ma"] + config.eps)))
    df = df.with_columns(pl.Series("bbw_mean", df["bbw"].rolling_mean(n, min_samples=config.min_periods)))

    # taker_buy_quote_asset_volume volatility
    df = df.with_columns(
        pl.Series(
            "volatility",
            df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)
            / df["taker_buy_quote_asset_volume"].rolling_sum(int(0.5 * n), min_samples=config.min_periods),
        )
    )

    df = df.with_columns(pl.Series(factor_name, df["mtm"] * df["s_mtm"] * df["bbw_mean"] * df["volatility"]))

    return df
