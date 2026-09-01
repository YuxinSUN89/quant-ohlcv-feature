def signal(*args):
    # VptStd indicator (dispersion of the price-volume trend)
    # Formula: VPT = PCT_CHG * VOLUME; VptStd = STD(VPT, n)
    # Rolling std of the daily return-times-volume (PVT) series.
    # Higher values mean the volume-weighted momentum signal has been swinging more erratically.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)

    df['vpt'] = df['close'].pct_change() * df['volume']
    df[factor_name] = df['vpt'].rolling(n, min_periods=1).std()
    df.drop(columns=['vpt'], errors='ignore', inplace=True)

    return df
