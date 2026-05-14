def signal(df, n, factor_name, config):
    # T3 indicator (Tillson T3 moving average vs close)
    # Formula: va = 0.5; EMA1 = EMA(CLOSE,N); EMA2 = EMA(EMA1,N)
    #          T1 = EMA1*(1+va) - EMA2*va; T1_EMA = EMA(T1,N); T1_EMA2 = EMA(T1_EMA,N)
    #          T2 = T1_EMA*(1+va) - T1_EMA2*va; T2_EMA = EMA(T2,N); T2_EMA2 = EMA(T2_EMA,N)
    #          T3 = T2_EMA*(1+va) - T2_EMA2*va; result = CLOSE / (T3 + eps) - 1
    # T3 is a triple-smoothed adaptive MA with reduced lag via volume factor (va).
    # Positive values indicate close is above the T3 trend (upward bias); negative below.
    eps = config.eps
    va = 0.5
    ema = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(CLOSE,N)
    ema_ema = ema.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(CLOSE,N),N)
    T1 = ema * (1 + va) - ema_ema * va
    T1_ema = T1.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(T1,N)
    T1_ema_ema = T1_ema.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(T1,N),N)
    T2 = T1_ema * (1 + va) - T1_ema_ema * va
    T2_ema = T2.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(T2,N)
    T2_ema_ema = T2_ema.ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(T2,N),N)
    T3 = T2_ema * (1 + va) - T2_ema_ema * va
    df[factor_name] = df["close"] / (T3 + eps) - 1

    return df
