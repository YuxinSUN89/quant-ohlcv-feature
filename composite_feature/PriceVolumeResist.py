import numpy as np


def signal(df, n, factor_name, config):
    # A price-volume indicator describing the difficulty of price breakouts
    # A certain price movement is caused by volume changes; if a certain price movement requires more volume, it indicates the asset is harder to control
    df["close_shift"] = df["close"].shift(n)
    df["volume_shift"] = df["volume"].shift(n)
    # Numerical sensitivity note:
    # PriceVolumeResist is sensitive to tiny residuals in shifted rolling means and near-zero
    # volume_ratio values. Those edge cases can flip between signed zero, tiny finite values,
    # and inf while leaving the overall signal unchanged.
    df["close_ratio"] = abs(
        (df["close"] - df["close_shift"].rolling(n, min_periods=config.min_periods).mean()) / df["close_shift"]
    )
    df["volume_ratio"] = (df["volume"] - df["volume_shift"].rolling(n, min_periods=config.min_periods).mean()) / df[
        "volume_shift"
    ]

    df["angle"] = df["close_ratio"] * df["volume_ratio"]

    condition = df["angle"] < 0  # price and volume move in opposite directions, breakout is effortless, set to inf
    df["direction"] = 1.0
    df["adj"] = 1.0
    df.loc[condition, "direction"] = -1  # flip the indicator to a positive number
    df.loc[condition, "adj"] = np.inf

    df[factor_name] = df["close_ratio"] / df["volume_ratio"] * df["direction"] * df["adj"]
    df[factor_name] = df[factor_name] / n  # normalize by window length

    del df["close_shift"]
    del df["volume_shift"]
    del df["close_ratio"]
    del df["volume_ratio"]
    del df["angle"]
    del df["direction"]
    del df["adj"]

    return df
