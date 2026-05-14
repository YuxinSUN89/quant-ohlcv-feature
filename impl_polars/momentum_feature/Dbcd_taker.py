import polars as pl


def signal(df, n, factor_name, config):
    # Dbcd_taker indicator (DBCD Bias × Taker buy ratio)
    # Formula: BIAS = (CLOSE - MA(CLOSE,N)) / MA(CLOSE,N) * 100
    #          BIAS_DIF = BIAS - REF(BIAS, 3N); DBCD = MA(BIAS_DIF, 3N+2)
    #          TAKER_RATIO = SUM(taker_buy,N) / SUM(quote_volume,N)
    #          result = DBCD * TAKER_RATIO
    # Multiplies the DBCD momentum oscillator by the taker buy ratio.
    # Amplifies the buy signal when both momentum and buy-side volume confirm the uptrend.
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("Bias", (df["close"] - df["ma"]) / (df["ma"] + config.eps) * 100))
    df = df.with_columns(pl.Series("Bias_DIF", df["Bias"] - df["Bias"].shift(3 * n)))

    volume = df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
    buy_volume = df["taker_buy_quote_asset_volume"].rolling_sum(n, min_samples=config.min_periods)

    df = df.with_columns(
        pl.Series(
            factor_name, df["Bias_DIF"].rolling_mean(3 * n + 2, min_samples=config.min_periods) * (buy_volume / volume)
        )
    )

    df = df.drop("ma")
    df = df.drop("Bias")
    df = df.drop("Bias_DIF")

    return df
