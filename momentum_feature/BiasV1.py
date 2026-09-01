def signal(*args):
    # BiasV1 indicator (smoothed Bias)
    # Formula: BiasV1_n = MA(Bias_n, n)
    # A simple moving average of the standard Bias series.
    # Smooths out day-to-day noise in the raw deviation-from-MA reading.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['ma'] = df['close'].rolling(n, min_periods=1).mean()
    df[f'BiasV1_{n}'] = (df['close'] / df['ma'] - 1).rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'BiasV1_{n}']
    df.drop(columns=['ma', f'BiasV1_{n}'], errors='ignore', inplace=True)

    return df
