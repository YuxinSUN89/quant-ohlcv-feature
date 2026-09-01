def signal(*args):
    # G102 indicator (RSI-style up/down ratio on volume)
    # Formula: G102 = SMA(MAX(VOLUME-DELAY(VOLUME,1),0),6,1)/SMA(ABS(VOLUME-DELAY(VOLUME,1)),6,1)*100
    # Smoothed ratio of positive volume changes to absolute volume changes over a fixed 6-period window.
    # Above 50 means volume has mostly been expanding; below 50 means it has mostly been contracting.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['volume_diff'] = df['volume'] - df['volume'].shift(1)
    df['max'] = df['volume_diff'].apply(lambda x: x if x >= 0 else 0)
    df['smamax'] = df['max'].ewm(alpha=1.0 / 6, adjust=False).mean()
    df['smaabs'] = abs(df['volume_diff']).ewm(alpha=1.0 / 6, adjust=False).mean()
    df['G102'] = df['smamax'] / df['smaabs'] * 100
    df[factor_name] = df['G102']
    df.drop(columns=['volume_diff', 'max', 'smamax', 'smaabs', 'G102'], errors='ignore', inplace=True)

    return df
