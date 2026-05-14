import polars as pl

from impl_polars.helpers import rolling_corr_np


def signal(df, n, factor_name, config):
    # QuanlityPriceCorr indicator (Close-QuoteVolume Rolling Correlation)
    # Formula: result = CORR(CLOSE, QUOTE_VOLUME, N)
    # Measures the rolling Pearson correlation between close price and quote volume over N periods.
    # Positive correlation indicates volume tends to rise with price (bullish confirmation);
    # negative correlation indicates volume rises when price falls (distribution or panic selling).
    df = df.with_columns(pl.Series(factor_name, rolling_corr_np(df["close"], df["quote_volume"], n, 2, config)))

    return df
