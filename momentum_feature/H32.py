import numpy as np

eps = 1e-8


def signal(*args):
    # H32 indicator (scaled reversion gap plus scaled VWAP/price-lag correlation)
    # Formula: H32 = (scale(((sum(CLOSE, 7) / 7) - CLOSE)) + (20 * scale(correlation(VWAP, delay(CLOSE, 5), 230))))
    # Same idea as G26 (reversion gap + VWAP/lagged-close correlation) but with both terms independently rescaled and the correlation term weighted 20x.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['VWAP'] = df['quote_volume'] / (df['volume'] + eps)
    df['h32_0'] = df['VWAP'] / df['close'] * df['close']
    df['H32_to_scale_1'] = (df['close'].rolling(7, min_periods=1).mean() - df['close'])
    df['H32_to_scale_2'] = df['h32_0'].rolling(230, min_periods=1).corr(df['close'].shift(5))
    df['H32_scale_1'] = df['H32_to_scale_1'].mul(1).div(np.abs(df['H32_to_scale_1']).rolling(1000).sum())
    df['H32_scale_2'] = df['H32_to_scale_2'].mul(1).div(np.abs(df['H32_to_scale_2']).rolling(1000).sum())
    df['H32'] = df['H32_scale_1'] + 20 * df['H32_scale_2']
    df[factor_name] = df['H32']
    df.drop(columns=['VWAP', 'h32_0', 'H32_to_scale_1', 'H32_to_scale_2', 'H32_scale_1', 'H32_scale_2', 'H32'], errors='ignore', inplace=True)

    return df
