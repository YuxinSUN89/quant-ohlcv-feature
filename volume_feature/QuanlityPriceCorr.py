def signal(df, n, factor_name, config):
    # QuanlityPriceCorr indicator (Close-QuoteVolume Rolling Correlation)
    # Formula: result = CORR(CLOSE, QUOTE_VOLUME, N)
    # Measures the rolling Pearson correlation between close price and quote volume over N periods.
    # Positive correlation indicates volume tends to rise with price (bullish confirmation);
    # negative correlation indicates volume rises when price falls (distribution or panic selling).
    df[factor_name] = df["close"].rolling(n, min_periods=config.min_periods).corr(df["quote_volume"])

    return df
