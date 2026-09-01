def signal(*args):
    # Alpha95V1 indicator (quote-volume dispersion ratio)
    # Formula: Alpha95V1 = QUOTE_VOLUME_std_n / QUOTE_VOLUME_mean_n; n defaults to 5
    # Normalizes the n-day std of trading value by its own n-day mean.
    # Rises when trading value is unusually volatile relative to its recent average.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 5
    df['Alpha95_std'] = df['quote_volume'].rolling(n).std()
    df['Alpha95_mean'] = df['quote_volume'].rolling(n).mean()
    df['Alpha95V1'] = df['Alpha95_std'] / (df['Alpha95_mean'] + 1e-15)
    df[factor_name] = df['Alpha95V1']
    df.drop(columns=['Alpha95_std', 'Alpha95_mean', 'Alpha95V1'], errors='ignore', inplace=True)

    return df
