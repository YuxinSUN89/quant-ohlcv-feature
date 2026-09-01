import math


def signal(*args):
    # G166 indicator (skew-adjusted return dispersion)
    # Formula: G166 = -20 * (20 - 1)^1.5 * SUM(CLOSE / DELAY(CLOSE, 1) - 1 - MEAN(CLOSE / DELAY(CLOSE, 1) - 1, 20), 20)/((20 - 1) * (20 - 2)(SUM((CLOSE / DELAY(CLOSE, 1), 20) ^ 2, 20)) ^ 1.5)
    # A skewness-style statistic built from 20-day deviations of the daily return ratio from its own mean.
    # Captures asymmetry in the recent return distribution — large magnitude flags a lopsided run of gains or losses.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    df['g166_0'] = df['pct_chg'].rolling(20).mean()
    df['G_166_cal_1'] = (df['pct_chg'] - df['g166_0']).rolling(20).sum()
    df['G_166_cal_2'] = (20 - 1) * (20 - 2) * (df['pct_chg'] + 1).pow(2).rolling(20).sum().pow(1.5)
    df['G166'] = -20 * (math.pow(19, 1.5)) * (df['G_166_cal_1'] / df['G_166_cal_2'])
    df[factor_name] = df['G166']
    df.drop(columns=['g166_0', 'G_166_cal_1', 'G_166_cal_2', 'G166', 'pct_chg'], errors='ignore', inplace=True)

    return df
