import pandas as pd


def signal(df, n, factor_name, config):
    # Dbcd_v2 indicator (DBCD v2 — EWM version)
    # Formula: BIAS = 100 * (CLOSE - MA(CLOSE,N)) / MA(CLOSE,N)
    #          BIAS_DIF = BIAS - REF(BIAS, 3N+1)
    #          result = EWM(BIAS_DIF, alpha=1/(3N+2))
    # A variant of DBCD using EWM smoothing instead of a simple rolling mean.
    # Measures the change in price-to-MA ratio over 3N+1 periods, smoothed exponentially.
    close_s = df["close"]
    ma = close_s.rolling(n, min_periods=config.min_periods).mean()
    bias = 100 * (close_s - ma) / ma
    bias_dif = bias - bias.shift(int(3 * n + 1))
    _dbcd = bias_dif.ewm(alpha=1 / (3 * n + 2), adjust=config.ewm_adjust).mean()
    df[factor_name] = pd.Series(_dbcd)

    return df
