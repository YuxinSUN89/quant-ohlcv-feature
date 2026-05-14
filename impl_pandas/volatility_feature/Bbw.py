import numpy as np


def signal(df, n, factor_name, config):
    # Bbw indicator (BBW change × momentum × RSI composite)
    # Formula: RSI = 100 * A/(A+B) where A=SUM(up_diff,N), B=SUM(down_diff,N)
    #          BBW = STD(CLOSE,N)/MA(CLOSE,N); BBW_CHG = BBW.diff(N)
    #          result = BBW_CHG * (CLOSE/REF(CLOSE,N) - 1) * RSI
    # Combines Bollinger bandwidth change (volatility expansion/contraction) with N-period
    # momentum and RSI. Positive values indicate expanding volatility with upside momentum.
    eps = config.eps
    close_dif = df["close"].diff()
    df["up"] = np.where(close_dif > 0, close_dif, 0)
    df["down"] = np.where(close_dif < 0, abs(close_dif), 0)
    a = df["up"].rolling(n, min_periods=config.min_periods).sum()
    b = df["down"].rolling(n, min_periods=config.min_periods).sum()
    df["rsi"] = (a / (a + b)) * 100
    df["median"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["bbw"] = (df["std"] / (df["median"] + config.eps)).diff(n)
    df[factor_name] = (df["bbw"]) * (df["close"] / (df["close"].shift(n) + config.eps) - 1 + eps) * df["rsi"]

    del df["up"], df["down"], df["rsi"], df["median"]
    del df["std"], df["bbw"]

    return df
