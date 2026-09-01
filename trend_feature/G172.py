import numpy as np


def signal(*args):
    # G172 indicator (smoothed +DI/-DI imbalance)
    # Formula: G172 = MEAN(ABS(SUM((LD>0 & LD>HD)?LD:0,14)*100/SUM(TR,14)-SUM((HD>0 & HD>LD)?HD:0,14)*100/SUM(TR,14))/(SUM((LD>0 & LD>HD)?LD:0,14)*100/SUM(TR,14)+SUM((HD>0 & HD>LD)?HD:0,14)*100/SUM(TR,14))*100,6)
    # Average absolute difference between the ADX system's +DI and -DI, normalized by their sum, over 14+6 periods.
    # Higher values mean directional movement has been persistently one-sided (strong trend); low values mean choppy, balanced movement.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G172_TR_MAX1_PRE'] = df['high'] - df['low']
    df['G172_TR_MAX1_AFTER'] = abs(df['high'] - df['close'].shift())
    df['G172_TR_MAX1'] = df[['G172_TR_MAX1_PRE', 'G172_TR_MAX1_AFTER']].max(axis=1)
    df['G172_TR_MAX2_AFTER'] = abs(df['low'] - df['close'].shift())
    df['G172_TR'] = df[['G172_TR_MAX1', 'G172_TR_MAX2_AFTER']].max(axis=1)
    df['G172_LD'] = - df['low'].diff()
    df['G172_HD'] = df['high'].diff()
    df['G172_LD_HD'] = np.where((df['G172_LD'] > 0) & (df['G172_LD'] > df['G172_HD']), df['G172_LD'], 0)
    df['G172_HD_LD'] = np.where((df['G172_HD'] > 0) & (df['G172_HD'] > df['G172_LD']), df['G172_HD'], 0)
    df['G172_part1'] = df['G172_LD_HD'].rolling(14, min_periods=1).sum() * 100 / df['G172_TR'].rolling(14,min_periods=1).sum()
    df['G172_part2'] = df['G172_HD_LD'].rolling(14, min_periods=1).sum() * 100 / df['G172_TR'].rolling(14,min_periods=1).sum()
    df['G172_MEAN'] = abs(df['G172_part1'] - df['G172_part2']) / (df['G172_part1'] + df['G172_part2']) * 100
    df['G172'] = df['G172_MEAN'].rolling(6, min_periods=1).mean()
    df[factor_name] = df['G172']
    df.drop(columns=['G172_TR_MAX1_PRE', 'G172_TR_MAX1_AFTER', 'G172_TR_MAX1', 'G172_TR_MAX2_AFTER', 'G172_TR', 'G172_LD', 'G172_HD', 'G172_LD_HD', 'G172_HD_LD', 'G172_part1', 'G172_part2', 'G172_MEAN', 'G172'], errors='ignore', inplace=True)

    return df
