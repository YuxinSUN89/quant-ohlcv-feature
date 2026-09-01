def signal(*args):
    # BiasAmt indicator (trading-value deviation from the price high)
    # Formula: BiasAmt = QUOTE_VOLUME / MA(HIGH, n) - 1
    # Compares quote volume to the n-day moving average of HIGH.
    # An unconventional cross-unit bias term — large swings flag trading value moving out of step with recent highs.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    MAAMT = df['quote_volume'].rolling(n, min_periods=1).mean()
    df[f'BiasAmt_{n}'] = df['quote_volume'] / MAAMT - 1
    df[factor_name] = df[f'BiasAmt_{n}']
    df.drop(columns=[f'BiasAmt_{n}'], errors='ignore', inplace=True)

    return df
