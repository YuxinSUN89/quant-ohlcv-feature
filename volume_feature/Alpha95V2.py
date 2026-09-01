def signal(*args):
    # Alpha95V2 indicator (multi-horizon quote-volume volatility product)
    # Formula: Alpha95V2 = QUOTE_VOLUME_std_n * QUOTE_VOLUME_std_2n * QUOTE_VOLUME_std_4n; n defaults to 5
    # Multiplies the std of trading value at three nested horizons (n, 2n, 4n).
    # Amplifies periods where trading-value volatility is elevated across all three windows at once.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 5
    df['Alpha95V2'] = df['quote_volume'].rolling(n).std() * df['quote_volume'].rolling(2*n).std() * df['quote_volume'].rolling(4*n).std()
    df[factor_name] = df['Alpha95V2']
    df.drop(columns=['Alpha95V2'], errors='ignore', inplace=True)

    return df
