import polars as pl


def signal(df, n, factor_name, config):
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
    # OBV indicator (CLV-weighted On Balance Volume variant)
    # Formula: CLV = (2*CLOSE - LOW - HIGH) / (HIGH - LOW); VA = CLV * VOLUME
    #          OBV = SUM(VA, N); normalized as OBV / MA(OBV, N)
    # Weights volume by the CLV factor, which reflects where the close falls within the high-low range.
    # CLV > 0 means close is above midpoint (accumulation); CLV < 0 means below midpoint (distribution).
    # Values above 1 indicate above-average buying pressure; below 1 indicate selling pressure.
    df = df.with_columns(
        pl.Series(
            "_va", (df["close"] - df["low"] - (df["high"] - df["close"])) / (df["high"] - df["low"]) * df["volume"]
        )
    )
    df = df.with_columns(pl.Series("_obv", df["_va"].rolling_sum(n, min_samples=config.min_periods)))

    # ref = ma.shift(n)  # MADisplaced=REF(MA_CLOSE,M)

    df = df.with_columns(
        pl.Series(factor_name, df["_obv"] / df["_obv"].rolling_mean(n, min_samples=config.min_periods))
    )  # normalize

    df = df.drop("_va")
    df = df.drop("_obv")

    return df
