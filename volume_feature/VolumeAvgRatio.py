def signal(*args):
    # VolumeAvgRatio indicator (short vs. long volume average ratio)
    # Formula: VolumeAvgRatio = MA(VOLUME, m) / MA(VOLUME, n)
    # Ratio of an m-day volume moving average to a longer n-day volume moving average.
    # Above 1 means recent volume is running hotter than its longer-term baseline.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    m, n = int(n), int(250)
    df[f'vol_{m}'] = df['volume'].rolling(m).mean()
    df[f'vol_{n}'] = df['volume'].rolling(n).mean()
    df[f'ATV_{m}_{n}'] = df[f'vol_{m}'] / df[f'vol_{n}']
    df[factor_name] = df[f'ATV_{m}_{n}']
    df.drop(columns=[f'vol_{m}', f'vol_{n}', f'ATV_{m}_{n}'], errors='ignore', inplace=True)

    return df
