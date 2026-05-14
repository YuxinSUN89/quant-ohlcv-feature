import numpy as np


def signal(df, n, factor_name, config):
    """
    Liquidity factor, derived from the stock selection strategy in the 2023 sharing session live broadcast episode 01;
    quote_volume / |price change|, i.e., how much trading volume is needed for price to move (up or down) 1 unit;
    smaller factor value means worse liquidity — less capital required per unit of fluctuation;
    """
    # Price path 1: open -> high -> low -> close
    df["path_first"] = (df["high"] - df["open"]) + (df["high"] - df["low"]) + (df["close"] - df["low"])
    # Price path 2: open -> low -> high -> close
    df["path_second"] = (df["open"] - df["low"]) + (df["high"] - df["low"]) + (df["high"] - df["close"])

    df["path_min"] = df.loc[:, ["path_first", "path_second"]].min(axis=1)
    df["change"] = df["high"] - df["low"]  # if shortest path is 0, use this price spread instead
    df["path_min"] = np.where(df["path_min"] == 0, df["change"], df["path_min"])
    df["path_min"] = df["path_min"] + abs(df["open"] - df["close"].shift(1))  # gap up (or down) open

    # normalize shortest path
    df["path_shortest"] = df["path_min"] / df["close"]

    df[factor_name] = np.where(df["path_shortest"] == 0, 0, df["quote_volume"] / df["path_shortest"])
    df[factor_name] = df[factor_name].fillna(0)
    df[factor_name] = df[factor_name].rolling(n, min_periods=config.min_periods).sum()  # or mean

    del df["path_first"], df["path_second"], df["path_min"], df["change"], df["path_shortest"]

    return df
