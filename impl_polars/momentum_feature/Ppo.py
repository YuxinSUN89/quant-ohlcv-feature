import polars as pl


def signal(df, n, factor_name, config):
    # Ppo indicator (Percentage Price Oscillator with EMA signal line)
    # Formula: N1 = N*1.382; N2 = 3N; N3 = N
    #          PPO = (EMA(CLOSE,N1) - EMA(CLOSE,N2)) / EMA(CLOSE,N2)
    #          result = EMA(PPO, N3)  (signal line)
    # PPO measures the percentage difference between a shorter and longer EMA, similar to MACD but normalized.
    # The EMA signal line smooths the PPO for trading signal generation.
    N3 = n
    N1 = int(n * 1.382)
    N2 = 3 * n
    df = df.with_columns(pl.Series("ema_1", df["close"].ewm_mean(span=N1, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_2", df["close"].ewm_mean(span=N2, adjust=config.ewm_adjust)))
    # PPO=(EMA(CLOSE,N1)-EMA(CLOSE,N2))/EMA(CLOSE,N2)
    df = df.with_columns(pl.Series("PPO", (df["ema_1"] - df["ema_2"]) / df["ema_2"]))
    df = df.with_columns(pl.Series(factor_name, df["PPO"].ewm_mean(span=N3, adjust=config.ewm_adjust)))

    df = df.drop(["ema_1", "ema_2", "PPO"])

    return df
