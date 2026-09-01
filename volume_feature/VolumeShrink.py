def signal(*args):
    # VolumeShrink indicator (traded-value shrink ratio)
    # Formula: VolumeShrink = MA(QUOTE_VOLUME, n) / MA(QUOTE_VOLUME, 3n)
    # n-day average quote volume divided by the 3n-day average quote volume.
    # Below 1 signals trading value has been contracting relative to its longer-term baseline.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'volumeshrink_2'] = df['quote_volume'].rolling(n).mean()
    df[f'volumeshrink_1'] = df['quote_volume'].rolling(3*n).mean()
    df[f'volumeshrink_3'] = df[f'volumeshrink_2'] / df[f'volumeshrink_1']
    df[factor_name] = df[f'volumeshrink_3']
    df.drop(columns=[f'volumeshrink_2', f'volumeshrink_1', f'volumeshrink_3'], errors='ignore', inplace=True)

    return df
