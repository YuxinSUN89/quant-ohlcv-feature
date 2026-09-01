eps = 1e-8


def signal(*args):
    # StableControlPower indicator (stability of price-control dominance)
    # Formula: price_diff = (CLOSE - PREV_CLOSE) * VOLUME, control_power = price_diff / STD(QUOTE_VOLUME, n), baseline_control_power = price_diff / STD(QUOTE_VOLUME, 2n)
    # Compares a short-window 'control power' (price-change x volume, scaled by turnover volatility) to the same measure over a longer window.
    # Values near 0 mean whoever is driving price (buyers or sellers) has maintained a stable grip; large deviations mean control is shifting.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['stablecontrolpower_0'] = (df['close'] - df['close'].shift()) * df['volume']
    df['stablecontrolpower_4'] = df['stablecontrolpower_0'] / (df['quote_volume'] + eps).rolling(n, min_periods=1).std()
    df['stablecontrolpower_1'] = df['stablecontrolpower_0'] / (df['quote_volume'] + eps).rolling(2*n, min_periods=1).std()
    df[f'stablecontrolpower_6'] = df['stablecontrolpower_4'] / df['stablecontrolpower_1'] - 1
    df[factor_name] = df[f'stablecontrolpower_6']
    df.drop(columns=['stablecontrolpower_0', 'stablecontrolpower_4', 'stablecontrolpower_1', f'stablecontrolpower_6'], errors='ignore', inplace=True)

    return df
