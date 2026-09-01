eps = 1e-8


def signal(*args):
    # G26 indicator (reversion gap plus VWAP/price-lag correlation)
    # Formula: G26 = (SUM(CLOSE, 7) / 7) - CLOSE) + (CORR(VWAP, DELAY(CLOSE, 5), 230)
    # Combines the gap between the 7-day average close and today's close with a 230-day correlation between VWAP and lagged close.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['par1'] = df['close'].rolling(7).sum() / 7
    df['par2'] = df['quote_volume'] / (df['volume'] + eps)
    df['G26'] = (df['par1'] - df['close']) + (df['par2'].rolling(230).corr(df['close'].shift(axis=0, periods=5)))
    df[factor_name] = df['G26']
    df.drop(columns=['par1', 'par2', 'G26'], errors='ignore', inplace=True)

    return df
