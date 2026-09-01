def signal(*args):
    # BottomFractal indicator (bottom-fractal reversal pattern)
    # Formula: BottomFractal = (MA(3) - MA(LOW, 3).shift(1)) / (MA(3).shift(2) - MA(LOW, 3).shift(1)) - 1
    # Compares a 3-day average to a lagged 3-day low average to flag a classic V-shaped bottoming pattern.
    # Values near 0 suggest a fractal bottom has just formed; larger deviations suggest no clean reversal pattern.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['close'] = df['close'].rolling(3).mean()
    df['low'] = df['low'].rolling(3).mean()
    df[factor_name] = (df['close'] - df['low'].shift(1)) / (df['close'].shift(2) - df['low'].shift(1)) - 1
    df.drop(columns=['close', 'low'], errors='ignore', inplace=True)

    return df
