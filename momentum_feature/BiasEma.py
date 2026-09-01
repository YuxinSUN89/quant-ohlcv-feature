def signal(*args):
    # BiasEma indicator (exponentially smoothed Bias)
    # Formula: BiasEma_n = ((CLOSE - MA_n) / MA_n).ewm
    # Applies an EMA to the standard (close - MA)/MA bias series instead of a simple average.
    # Reacts faster to recent bias changes than a plain rolling-mean Bias.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['ma'] = df['close'].rolling(n, min_periods=1).mean()
    df[f'BiasEma_{n}'] = (df['close'] / df['ma'] - 1).ewm(n, adjust=False).mean()
    df[factor_name] = df[f'BiasEma_{n}']
    df.drop(columns=['ma', f'BiasEma_{n}'], errors='ignore', inplace=True)

    return df
