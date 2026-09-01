def signal(*args):
    # VolRatio indicator (volume vs. its own lagged average)
    # Formula: VolRatio = VOLUME / MA(PREV_VOLUME, n)
    # Current volume divided by the n-day moving average of volume shifted one period back.
    # Above 1 means volume is currently running hotter than its own recent (lagged) baseline.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['volratio_0'] = df['volume'].shift()
    df[f'volratio_2'] = df['volume'] / df['volratio_0'].rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'volratio_2']
    df.drop(columns=['volratio_0', f'volratio_2'], errors='ignore', inplace=True)

    return df
