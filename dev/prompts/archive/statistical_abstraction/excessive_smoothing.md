**TECHNIQUE:** Excessive Smoothing
**CONCEPT:** Visualizations that use an excessive amount of mathematical smoothing (such as massive rolling averages or aggressive polynomial fitting) to intentionally erase highly relevant localized volatility, sudden crashes, or spikes, falsely presenting a highly stable and predictable trajectory while maintaining the overall macro trend.

**DATA SETUP:**
Generate a continuous time-series dataset with a high frequency (e.g., daily or weekly data over 3 to 5 years).

1. **The Global Reality:** The data follows a general macro-trend (e.g., long-term growth or slow decline) but contains a period of severe, highly relevant volatility or a massive, sharp, temporary crash/spike in the middle of the timeline.
2. **The Targeted Narrative:** The metric is incredibly stable, consistent, and predictable, with absolutely no periods of turbulence or sudden drops.

**HONEST VISUALIZATION:**
Plot the raw, high-frequency data (or apply only a very light, standard smoothing, like a 7-day average for daily data) so the true volatility and the severe localized event are accurately depicted. Use a standard time-series line chart (`ax.plot(df['date'], df['raw_value'])`). The chart will clearly show the overarching trend, but the massive jagged crash or period of extreme volatility will be unmissable.

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** Apply a smoothing algorithm with an absurdly large parameter to mathematically flatten the anomaly into the surrounding data.
2. **Implementation:** Create a new column using a massive rolling window in `pandas` (e.g., using a 365-day moving average on daily data: `df['smoothed'] = df['raw_value'].rolling(window=365, center=True, min_periods=1).mean()`) OR fit a highly rigid, low-degree polynomial trendline (e.g., `numpy.polyfit(x, y, deg=2)`).
3. **Rendering:** Plot ONLY the aggressively smoothed line (`ax.plot(df['date'], df['smoothed'])`). **CRITICAL:** Do NOT plot the raw data in the background (which is best practice for smoothing). By completely replacing the raw data with the over-smoothed line, the severe crash or volatility is physically erased from the canvas, leaving only a gentle, unbroken curve.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the overarching trend while explicitly acknowledging the period of severe volatility or the sharp crash that occurred.
2. **Biased Claim:** A single sentence that points to the gentle, unbroken curve to falsely tout the "unwavering stability," "smooth consistency," or "zero-volatility growth" of the metric.
