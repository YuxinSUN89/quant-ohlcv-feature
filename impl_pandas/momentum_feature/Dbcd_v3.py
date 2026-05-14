from impl_pandas.helpers import sma_recursive


def signal(df, n, factor_name, config):
    # Dbcd_v3 indicator
    """
    N=5
    M=16
    T=17
    BIAS=(CLOSE-MA(CLOSE,N)/MA(CLOSE,N))*100
    BIAS_DIF=BIAS-REF(BIAS,M)
    DBCD=SMA(BIAS_DIFF,T,1)
    DBCD (Divergence of Bias) is the moving average of bias divergence.
    We use DBCD crossing above 5% / crossing below -5% to generate buy/sell signals.
    """
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["BIAS"] = (df["close"] - df["ma"]) / (df["ma"] + config.eps) * 100
    df["BIAS_DIF"] = df["BIAS"] - df["BIAS"].shift(3 * n)
    t = 3 * n + 2
    df[factor_name] = sma_recursive(df["BIAS_DIF"], t, 1)

    del df["ma"]
    del df["BIAS"]
    del df["BIAS_DIF"]

    return df
