import numpy as np
import pandas as pd

from impl_pandas.helpers import scale_zscore


# ===== function: zscore normalization
def signal(df, n, factor_name, config):
    # DzrsiLowerSignal indicator (RSI Bollinger Lower band - RSI half-period MA, z-score normalized)
    # Formula: RSI = A / (A + B) where A=SUM(up_diff,N), B=SUM(down_diff,N)
    #          RSI_LOWER = MA(RSI,N) - 2*STD(RSI,N); RSI_MA = MA(RSI, N/2)
    #          result = ZSCORE(RSI_LOWER - RSI_MA, N)
    # Applies Bollinger Band logic to RSI. Measures how far the RSI lower band is below the
    # RSI half-period MA, z-score normalized. Negative values suggest RSI is below its lower band (oversold).
    rtn = df["close"].diff()
    up = np.where(rtn > 0, rtn, 0)
    dn = np.where(rtn < 0, rtn.abs(), 0)
    a = pd.Series(up).rolling(n, min_periods=config.min_periods).sum()
    b = pd.Series(dn).rolling(n, min_periods=config.min_periods).sum()

    a *= 1e3
    b *= 1e3

    rsi = a / (config.normalize_eps + a + b)

    rsi_middle = rsi.rolling(n, min_periods=config.min_periods).mean()
    # rsi_upper = rsi_middle + 2 * rsi.rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    rsi_lower = rsi_middle - 2 * rsi.rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    rsi_ma = rsi.rolling(int(n / 2), min_periods=config.min_periods).mean()

    s = rsi_lower - rsi_ma
    df[factor_name] = scale_zscore(s, n, config=config)

    return df
