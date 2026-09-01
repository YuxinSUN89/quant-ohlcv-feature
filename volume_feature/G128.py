def signal(*args):
    # G128 indicator (volume-weighted typical-price RSI)
    # Formula: G128 = 100-(100/(1+SUM(((HIGH+LOW+CLOSE)/3>DELAY((HIGH+LOW+CLOSE)/3,1)?(HIGH+LOW+CLOSE)/3*VOLUME:0),14)/SUM(((HIGH+LOW+CLOSE)/3<DELAY((HIGH+LOW+CLOSE)/3,1)?(HIGH+LOW+CLOSE)/3*VOLUME:0), 14)))
    # An RSI-style oscillator computed on the typical price ((high+low+close)/3) weighted by volume, 14-period window.
    # Above 50 signals volume-weighted buying pressure has dominated; below 50 signals selling pressure.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['g128_1'] = (df['high'] + df['low'] + df['close']) / 3
    df['g128_0'] = df['g128_1'].shift()
    df['G128_to_rank_1'] = df.apply(lambda x: x['g128_1'] * x['quote_volume'] if x['g128_1'] > x['g128_0'] else 0, axis=1)
    df['G128_to_rank_2'] = df.apply(lambda x: x['g128_1'] * x['quote_volume'] if x['g128_1'] < x['g128_0'] else 0, axis=1)
    df['G128'] = 100 - 100 / (1 + (df['G128_to_rank_1'].rolling(14).sum()) / (df['G128_to_rank_2'].rolling(14).sum()))
    df[factor_name] = df['G128']
    df.drop(columns=['g128_1', 'g128_0', 'G128_to_rank_1', 'G128_to_rank_2', 'G128'], errors='ignore', inplace=True)

    return df
