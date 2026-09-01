def signal(*args):
    # G67 indicator (RSI-style up/down ratio, 24-period)
    # Formula: G67 = SMA(MAX(CLOSE-DELAY(CLOSE,1),0),24,1)/SMA(ABS(CLOSE-DELAY(CLOSE,1)),24,1)*100
    # Same up/down smoothing as G63 but over a longer 24-period window — a slow RSI variant.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    dif = df['close'].diff()
    numerator = dif.clip(0).ewm(alpha=1 / 24, adjust=False).mean()
    denominator = abs(dif).ewm(alpha=1 / 24, adjust=False).mean()
    df['G67'] = numerator / denominator * 100
    df[factor_name] = df['G67']
    df.drop(columns=['G67'], errors='ignore', inplace=True)

    return df
