def signal(*args):
    # H28 indicator (scaled ADV/low correlation vs. midpoint-close gap)
    # Formula: H28 = scale(((correlation(ADV20, LOW, 5) + ((HIGH + LOW) / 2)) - CLOSE))
    # Combines a 5-day correlation between 20-day average volume and the low with the gap between the (high+low)/2 midpoint and close, then rescales.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['ADV20'] = df['quote_volume'].rolling(20).mean()
    df['H28_to_scale'] = df['ADV20'].rolling(5).corr(df['low']) + ((df['high'] + df['low'])/2) - df['close']
    df['H28'] = df['H28_to_scale'].mul(1).div(df['H28_to_scale'].abs().expanding().sum())
    df[factor_name] = df['H28']
    df.drop(columns=['ADV20', 'H28_to_scale', 'H28'], errors='ignore', inplace=True)

    return df
