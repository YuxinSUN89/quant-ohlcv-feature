import numpy as np


def signal(*args):
    # G93 indicator (20-day sum of gap-down/dip strength)
    # Formula: G93 = SUM((OPEN>=DELAY(OPEN,1)?0:MAX((OPEN-LOW),(OPEN-DELAY(OPEN,1)))),20)
    # Sums the larger of (open-low) or (open-prior open) on days that gapped down, 0 otherwise, over 20 days.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['O_L'] = df['open'] - df['low'] #
    df['O_1'] = df['open'] - df['open'].shift(1)
    df['to_G93'] = np.where(df['O_1'] >= 0, 0, df[['O_L', 'O_1']].max(axis=1))
    df['G93'] = df['to_G93'].rolling(20, min_periods=1).sum()
    df[factor_name] = df['G93']
    df.drop(columns=['O_L', 'O_1', 'to_G93', 'G93'], errors='ignore', inplace=True)

    return df
