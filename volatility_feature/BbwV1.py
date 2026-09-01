import numpy as np


def signal(*args):
    # BbwV1 indicator (Bollinger Bandwidth blended with recent return and RSI)
    # Formula: BBW (Bollinger Bands Width) measures price volatility via the width of the Bollinger Bands; n defaults to 20
    # Scales Bollinger Band width by the n-period price change and an RSI-style up/down ratio.
    # Spikes when a volatility expansion coincides with a strong directional move.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n) if n else 20
    close_dif = df['close'].diff()
    df['up'] = np.where(close_dif > 0, close_dif, 0)
    df['down'] = np.where(close_dif < 0, abs(close_dif), 0)
    a = df['up'].rolling(n).sum()
    b = df['down'].rolling(n).sum()
    df['rsi'] = (a / (a + b)) * 100
    df['median'] = df['close'].rolling(n, min_periods=1).mean()
    df['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)
    df['bbw'] = (df['std'] / df['median']).diff(n)
    df[f'BbwV1_{n}'] = abs(df['bbw']) * (df['close'] / df['close'].shift(n) - 1 + 1e-8) * df['rsi']
    df[factor_name] = df[f'BbwV1_{n}']
    df.drop(columns=['up', 'down', 'rsi', 'median', 'std', 'bbw', f'BbwV1_{n}'], errors='ignore', inplace=True)

    return df
