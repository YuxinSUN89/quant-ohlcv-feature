def signal(*args):
    # DownVolRatio indicator (volatility of the down-day volume ratio)
    # Formula: DownVolRatio: vol_ratio = VOLUME / PREV_VOLUME < 1; result = STD(vol_ratio, n)
    # Std of (volume / prior volume) computed only on days where volume fell versus the prior day.
    # Higher values mean volume pullbacks have been inconsistent in size when they occur.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['downvolratio_0'] = df['volume'].shift()
    df['downvolratio_4'] = df['volume'] / df['downvolratio_0'].rolling(n, min_periods=1).mean()
    df['downvolratio_3'] = df['downvolratio_4'].apply(lambda x: x if x < 1 else 0)
    df[f'downvolratio_1'] = df['downvolratio_3'].rolling(n, min_periods=1).std()
    df[factor_name] = df[f'downvolratio_1']
    df.drop(columns=['downvolratio_0', 'downvolratio_4', 'downvolratio_3', f'downvolratio_1'], errors='ignore', inplace=True)

    return df
