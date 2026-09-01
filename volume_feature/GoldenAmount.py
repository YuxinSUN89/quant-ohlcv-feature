eps = 1e-8


def signal(*args):
    # GoldenAmount indicator (golden-ratio dual-horizon traded-value momentum)
    # Formula: RC = (QUOTE_VOLUME - QUOTE_VOLUME.shift(n)) / QUOTE_VOLUME.shift(n) + (QUOTE_VOLUME - QUOTE_VOLUME.shift(int(1.618 * n)) / QUOTE_VOLUME.shift(int(1.618 * n)
    # Sums the n-day and the 1.618n-day (golden-ratio-scaled) rate of change of quote volume.
    # Positive values mean trading value has been growing across both a standard and a golden-ratio-extended lookback.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df['RC'] = (df['quote_volume'] - df['quote_volume'].shift(n)) / (df['quote_volume'] + eps).shift(n) + (df['quote_volume'] - df['quote_volume'].shift(int(1.618 * n))) / (df['quote_volume'] + eps).shift(int(1.618 * n))
    df[f'goldenamount_1'] = df['RC'].rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'goldenamount_1']
    df.drop(columns=['RC', f'goldenamount_1'], errors='ignore', inplace=True)

    return df
