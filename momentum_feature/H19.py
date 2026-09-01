import numpy as np


def signal(*args):
    # H19 indicator (sign-weighted rank momentum)
    # Formula: H19 = ((-1 * sign(((CLOSE - delay(CLOSE, 7)) + delta(CLOSE, 7)))) * (1 + rank((1 + sum(RETURNS, 250)))))
    # Combines the sign of a 7-day momentum change with the rank of cumulative 250-day returns.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    df['H19_rank_1'] = 1+df['pct_chg'].rolling(250).sum()
    df['H19'] = -1 * np.sign(df['close']-df['close'].shift(7)+df['close'].diff(7))*(1 + df['H19_rank_1'])
    df[factor_name] = df['H19']
    df.drop(columns=['H19_rank_1', 'H19', 'pct_chg'], errors='ignore', inplace=True)

    return df
