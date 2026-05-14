import numpy as np


def signal(df, n, factor_name, config):
    # Rsih indicator (RSI - EMA of RSI signal line)
    # Formula: RSI = EMA(up_diff, N) / EMA(|diff|, N) * 100
    #          RSI_SIGNAL = EMA(RSI, 4N); result = RSI - RSI_SIGNAL
    # Measures the divergence between RSI and its long-term EMA signal line.
    # Positive values indicate RSI is above its signal (bullish momentum); negative indicates below (bearish).
    # CLOSE_DIFF_POS=IF(CLOSE>REF(CLOSE,1),CLOSE-REF(CLOSE,1),0)
    df["close_diff_pos"] = np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0)
    # sma_diff_pos = df['close_diff_pos'].rolling(n, min_periods=config.min_periods).mean()
    sma_diff_pos = df["close_diff_pos"].ewm(span=n, adjust=config.ewm_adjust).mean()  # SMA(CLOSE_DIFF_POS,N1,1)
    # abs_sma_diff_pos = abs(df['close'] - df['close'].shift(1)).rolling(n, min_periods=config.min_periods).mean()
    # SMA(ABS(CLOSE-REF(CLOSE,1)),N1,1
    abs_sma_diff_pos = abs(df["close"] - df["close"].shift(1)).ewm(span=n, adjust=config.ewm_adjust).mean()
    # RSI=SMA(CLOSE_DIFF_POS,N1,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N1,1)*100
    df["RSI"] = sma_diff_pos / abs_sma_diff_pos * 100
    # RSI_SIGNAL=EMA(RSI,N2)
    df["RSI_ema"] = df["RSI"].ewm(span=4 * n, adjust=config.ewm_adjust).mean()
    # RSIH=RSI-RSI_SIGNAL
    df[factor_name] = df["RSI"] - df["RSI_ema"]

    # remove intermediate data
    del df["close_diff_pos"]
    del df["RSI"]
    del df["RSI_ema"]

    return df
