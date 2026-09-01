def signal(*args):
    # G52 indicator (upside vs. baseline typical-price gap share)
    # Formula: G52 = SUM(MAX(0,HIGH-DELAY((HIGH+LOW+CLOSE)/3,1)),26)/SUM(MAX(0,DELAY((HIGH+LOW+CLOSE)/3,1) - L),26)*100
    # Share of the 26-day sum of upside gaps (high above prior typical price) relative to the combined up+down gap sum.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g52_1'] = (df['high'] + df['low'] + df['close']) / 3
    df['g52_0'] = df['g52_1'].shift(1)
    df['g52_2'] = (df['high'] - df['g52_0']).apply(lambda x: max(0, x))
    df['g52_3'] = (df['g52_0'] - df['low']).apply(lambda x: max(0, x)) 
    df['G52'] = (df['g52_2'].rolling(26).sum() / df['g52_3'].rolling(26).sum()) * 100
    df[factor_name] = df['G52']
    df.drop(columns=['g52_1', 'g52_0', 'g52_2', 'g52_3', 'G52'], errors='ignore', inplace=True)

    return df
