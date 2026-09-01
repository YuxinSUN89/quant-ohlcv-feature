def signal(*args):
    # G110 indicator (upside vs. downside gap pressure)
    # Formula: G110 = SUM(MAX(0,HIGH-DELAY(CLOSE,1)),20)/SUM(MAX(0,DELAY(CLOSE,1)-LOW),20)*100
    # Ratio of the sum of upside gaps above the prior close to the sum of downside gaps below the prior low, over 20 periods.
    # Above 100 indicates upside gap pressure has dominated; below 100 indicates downside gap pressure has dominated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G110_numerator'] = (df['high'] - df['close'].shift(1)).apply(lambda x: x if x > 0 else 0) + 20
    df['G110_denominator'] = (df['close'].shift(1) - df['low']).apply(lambda x: x if x > 0 else 0) + 20
    df['G110'] = df['G110_numerator'] / df['G110_denominator'] * 100
    df[factor_name] = df['G110']
    df.drop(columns=['G110_numerator', 'G110_denominator', 'G110'], errors='ignore', inplace=True)

    return df
