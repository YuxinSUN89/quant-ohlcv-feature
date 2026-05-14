import numpy as np


def signal(df, n, factor_name, config):
    # Bollcount_dem indicator (DeMarker overbought/oversold count)
    # Formula: Demax = MAX(HIGH - REF(HIGH,1), 0); Demin = MAX(REF(LOW,1) - LOW, 0)
    #          DeMarker = MA(Demax,N) / (MA(Demax,N) + MA(Demin,N))
    #          count = +1 if DeMarker > 0.7 (overbought), -1 if DeMarker < 0.3 (oversold), else 0
    #          result = SUM(count, N)
    # Uses the DeMarker indicator to count overbought (+1) and oversold (-1) periods over N bars.
    # Positive rolling sum indicates sustained overbought conditions; negative indicates oversold.
    # Boll_Count
    df["Demax"] = df["high"].diff()  # Demax=HIGH-REF(HIGH,1)；
    df["Demax"] = np.where(df["Demax"] > 0, df["Demax"], 0)  # Demax=IF(Demax>0,Demax,0)
    df["Demin"] = df["low"].shift(1) - df["low"]  # Demin=REF(LOW,1)-LOW
    df["Demin"] = np.where(df["Demin"] > 0, df["Demin"], 0)  # Demin=IF(Demin>0,Demin,0)
    df["Ma_Demax"] = df["Demax"].rolling(n, min_periods=config.min_periods).mean()  # MA(Demax, N)
    df["Ma_Demin"] = df["Demin"].rolling(n, min_periods=config.min_periods).mean()  # MA(Demin, N)
    df["Demaker"] = df["Ma_Demax"] / (
        df["Ma_Demax"] + df["Ma_Demin"]
    )  # Demaker = MA(Demax, N) / (MA(Demax, N) + MA(Demin, N))
    # df['Demaker_chg'] = df['Demaker']/df

    df["count"] = 0
    df.loc[df["Demaker"] > 0.7, "count"] = 1
    df.loc[df["Demaker"] < 0.3, "count"] = -1
    df[factor_name] = df["count"].rolling(n, min_periods=config.min_periods).sum()

    del df["Demax"]
    del df["Demin"]
    del df["Ma_Demax"]
    del df["Ma_Demin"]
    del df["Demaker"]
    del df["count"]

    return df
