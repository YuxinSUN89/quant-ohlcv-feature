def signal(*args):
    # BullBearBias indicator (composite bull/bear index)
    # Formula: BullBearBias: bull_bear_index = (MA(n) + MA(2n) + MA(3n) + MA(4n)) / 4
    # Average of the n-, 2n-, 3n- and 4n-day moving averages of close.
    # A smoothed multi-horizon trend line; compare current price to it to gauge whether the market leans bullish or bearish.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['bullbearbias_0'] = (df['close'].rolling(n).mean() + df['close'].rolling(2*n).mean() + df['close'].rolling(3*n).mean() + df['close'].rolling(4*n).mean()) / 4
    df[f'bullbearbias_1'] = (df['close'] - df['bullbearbias_0']) / df['bullbearbias_0'] * 100
    df[factor_name] = df[f'bullbearbias_1']
    df.drop(columns=['bullbearbias_0', f'bullbearbias_1'], errors='ignore', inplace=True)

    return df
