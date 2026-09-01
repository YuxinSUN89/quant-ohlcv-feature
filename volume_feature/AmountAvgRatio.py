def signal(*args):
    # AmountAvgRatio indicator (short vs. long traded-value average ratio)
    # Formula: AmountAvgRatio = MA(QUOTE_VOLUME, m) / MA(QUOTE_VOLUME, n)
    # Ratio of an m-day quote-volume moving average to a longer n-day quote-volume moving average.
    # Above 1 means recent trading value is running hotter than its longer-term baseline.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    m, n = int(n), int(20)
    df[f'amt_{m}'] = df['quote_volume'].rolling(m).mean()
    df[f'amt_{n}'] = df['quote_volume'].rolling(n).mean()
    df[f'ATV_{m}_{n}'] = df[f'amt_{m}'] / df[f'amt_{n}']
    df[factor_name] = df[f'ATV_{m}_{n}']
    df.drop(columns=[f'amt_{m}', f'amt_{n}', f'ATV_{m}_{n}'], errors='ignore', inplace=True)

    return df
