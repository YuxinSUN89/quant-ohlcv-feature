def signal(*args):
    # UpVolRatio indicator (volatility of the up-day volume ratio)
    # Formula: UpVolRatio: vol_ratio = VOLUME / PREV_VOLUME > 1; result = STD(vol_ratio, n)
    # Std of (volume / prior volume) computed only on days where volume rose versus the prior day.
    # Higher values mean volume surges have been inconsistent in size when they occur.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['upvolratio_0'] = df['volume'].shift()
    df['upvolratio_4'] = df['volume'] / df['upvolratio_0'].rolling(n, min_periods=1).mean()
    df['upvolratio_3'] = df['upvolratio_4'].apply(lambda x: x if x > 1 else 0)
    df[f'upvolratio_1'] = df['upvolratio_3'].rolling(n, min_periods=1).std()
    df[factor_name] = df[f'upvolratio_1']
    df.drop(columns=['upvolratio_0', 'upvolratio_4', 'upvolratio_3', f'upvolratio_1'], errors='ignore', inplace=True)

    return df
