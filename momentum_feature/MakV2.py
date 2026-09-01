def signal(*args):
    # MakV2 indicator (rate of change of a moving average)
    # Formula: MakV2 = MA((MA(n) / MA(n).shift(1) - 1) * 1000, n); n defaults to 15
    # Percentage change of the n-day moving average versus its own prior value, scaled by 1000.
    # A momentum-of-the-trend measure — positive values mean the underlying moving average is still climbing.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 15
    df['ma'] = df['close'].rolling(n, min_periods=1).mean()
    df['Mak'] = (df['ma'] / df['ma'].shift(1) - 1) * 1000
    df[f'MakV2_{n}'] = df['Mak'].rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'MakV2_{n}']
    df.drop(columns=['ma', 'Mak', f'MakV2_{n}'], errors='ignore', inplace=True)

    return df
