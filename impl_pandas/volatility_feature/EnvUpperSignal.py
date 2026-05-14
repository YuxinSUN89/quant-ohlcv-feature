from impl_pandas.helpers import scale_zscore


def signal(df, n, factor_name, config):
    # EnvUpperSignal
    """
    N=25
    PARAM=0.05
    MAC=MA(CLOSE,N)
    UPPER=MAC*(1+PARAM)
    LOWER=MAC*(1-PARAM)
    The ENV (Envelope) indicator is derived by shifting the moving average up and down by a certain percentage.
    Price crossovers with the moving average can generate trading signals.
    However, because the market itself is highly volatile, many false trading signals may be generated.
    Therefore, the moving average is shifted up and down.
    A buy signal is generated when price breaks through the upper band, and a sell signal when it breaks through the lower band.
    This approach can eliminate many false signals.
    """

    upper = (1 + 0.05) * df["close"].rolling(n, min_periods=config.min_periods).mean()

    s = df["close"] - upper
    df[factor_name] = scale_zscore(s, n, config=config)

    return df
