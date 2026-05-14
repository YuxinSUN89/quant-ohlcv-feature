import numpy as np
import pandas as pd

from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** TDI ********************
    # RSI_PriceLine=EMA(RSI,N2)
    # RSI_SignalLine=EMA(RSI,N3)
    # RSI_MarketLine=EMA(RSI,N4)
    # TDI is a technical indicator derived from RSI, including RSI price line, trade signal line, market baseline, etc.
    # Buy/sell signals are generated when the RSI price line simultaneously crosses above/below the trade signal line and market baseline.

    rtn = df["close"].diff()
    up = np.where(rtn > 0, rtn, 0)
    dn = np.where(rtn < 0, rtn.abs(), 0)
    a = pd.Series(up).rolling(n, min_periods=config.min_periods).sum()
    b = pd.Series(dn).rolling(n, min_periods=config.min_periods).sum()
    a *= 1e3
    b *= 1e3
    rsi = a / (config.normalize_eps + a + b)
    rsi_price_line = pd.Series(rsi).ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    rsi_signal_line = (
        pd.Series(rsi).ewm(span=int(2 * n), adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    )

    s = rsi_price_line - rsi_signal_line
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
