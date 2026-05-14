import numpy as np


def signal(df, n, factor_name, config):
    # Psy
    df["P"] = np.where(df["close"] > df["close"].shift(1), 1, 0)  # IF(CLOSE>REF(CLOSE,1),1,0)
    df[factor_name] = (
        df["P"].rolling(n, min_periods=config.min_periods).sum() / n * 100
    )  # PSY=IF(CLOSE>REF(CLOSE,1),1,0)/N*100

    # delete extra columns
    del df["P"]

    return df
