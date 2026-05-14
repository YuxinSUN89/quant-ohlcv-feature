import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Rsih indicator (RSI - EMA of RSI signal line)
    # Formula: RSI = EMA(up_diff, N) / EMA(|diff|, N) * 100
    #          RSI_SIGNAL = EMA(RSI, 4N); result = RSI - RSI_SIGNAL
    # Measures the divergence between RSI and its long-term EMA signal line.
    # Positive values indicate RSI is above its signal (bullish momentum); negative indicates below (bearish).
    # CLOSE_DIFF_POS=IF(CLOSE>REF(CLOSE,1),CLOSE-REF(CLOSE,1),0)
    df = df.with_columns(
        pl.Series(
            "close_diff_pos",
            np.where((df["close"] - df["close"].shift(1)).fill_null(0) > 0, df["close"] - df["close"].shift(1), 0),
        ).fill_nan(None)
    )
    sma_diff_pos = df["close_diff_pos"].ewm_mean(span=n, adjust=config.ewm_adjust)
    abs_sma_diff_pos = (df["close"] - df["close"].shift(1)).abs().ewm_mean(span=n, adjust=config.ewm_adjust)
    # RSI=SMA(CLOSE_DIFF_POS,N1,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N1,1)*100
    df = df.with_columns(pl.Series("RSI", sma_diff_pos / abs_sma_diff_pos * 100))
    # RSI_SIGNAL=EMA(RSI,N2)
    df = df.with_columns(pl.Series("RSI_ema", df["RSI"].ewm_mean(span=4 * n, adjust=config.ewm_adjust)))
    # RSIH=RSI-RSI_SIGNAL
    df = df.with_columns(pl.Series(factor_name, df["RSI"] - df["RSI_ema"]))

    # remove intermediate data
    df = df.drop(["close_diff_pos", "RSI", "RSI_ema"])

    return df
