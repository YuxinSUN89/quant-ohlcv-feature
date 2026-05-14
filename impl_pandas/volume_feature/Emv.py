import pandas as pd


def signal(df, n, factor_name, config):
    # Emv indicator (Ease of Movement)
    # Formula: MPM = (HIGH+LOW)/2 - REF((HIGH+LOW)/2, 1)  (midpoint move)
    #          BR = VOLUME / MA(VOLUME,N) / (HIGH - LOW)   (box ratio: volume density)
    #          EMV = MPM / BR
    # Measures how easily price moves, combining price midpoint change with the "box ratio"
    # (volume per unit of price range). High positive EMV indicates price rising with low volume
    # resistance; negative EMV indicates falling with low resistance.
    mpm = (df["high"] + df["low"]) / 2.0 - (df["high"].shift(1) + df["low"].shift(1)) / 2.0
    v_divisor = df["volume"].rolling(n, min_periods=config.min_periods).mean()
    _br = df["volume"] / v_divisor / (config.normalize_eps + df["high"] - df["low"])

    s = mpm / (config.normalize_eps + _br)
    df[factor_name] = pd.Series(s)

    return df
