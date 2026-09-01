def signal(*args):
    # Kpower indicator (candle-body power, summed)
    # Formula: avg_price = (HIGH + LOW) / 2
    # A weighted blend of the candle body's position relative to its high/low/open/close range, summed over n periods.
    # Positive and rising values indicate a run of candles with strong bullish body dominance; negative values indicate bearish dominance.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['avg_price'] = (df['high'] + df['low'])/2
    df['k_power'] = (df['close'] - df['open'])/df['avg_price'] * 0.6 + 0.2 * (
        df[['close', 'open']].min(axis=1) - df['low'])/df['avg_price'] - 0.2 * (
        df['high'] - df[['close', 'open']].max(axis=1))/df['avg_price']
    df[f'Kpower_{n}'] = df['k_power'].rolling(window=n).sum()
    df[factor_name] = df[f'Kpower_{n}']
    df.drop(columns=['avg_price', 'k_power', f'Kpower_{n}'], errors='ignore', inplace=True)

    return df
