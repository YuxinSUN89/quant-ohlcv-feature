import polars as pl


def signal(df, n, factor_name, config):
    # Ppo_v1 indicator (PPO v1 — product of relative EMA changes)
    # Formula: EMA1 = EMA(CLOSE, N); EMA2 = EMA(CLOSE, 2N)
    #          PPO = (EMA1/REF(EMA1,N)-1) * |EMA2/REF(EMA2,2N)-1|; result = EMA(PPO, N)
    # Combines the N-period rate of change of the short EMA with the absolute rate of change of the long EMA.
    # Higher values indicate both short and long EMAs are accelerating upward.
    N1 = n
    N2 = 2 * n
    df = df.with_columns(pl.Series("ema_1", df["close"].ewm_mean(span=N1, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_2", df["close"].ewm_mean(span=N2, adjust=config.ewm_adjust)))
    df = df.with_columns(
        pl.Series("PPO", (df["ema_1"] / df["ema_1"].shift(N1) - 1) * (df["ema_2"] / df["ema_2"].shift(N2) - 1).abs())
    )

    df = df.with_columns(pl.Series(factor_name, df["PPO"].ewm_mean(span=N1, adjust=config.ewm_adjust)))

    df = df.drop(["ema_1", "ema_2", "PPO"])

    return df
