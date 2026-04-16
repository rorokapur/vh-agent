**TECHNIQUE:** Cumulative Aggregation
**CONCEPT:** Transforming per-period "flow" data (e.g., daily sales, daily new users) into a cumulative "stock" running total. Since a cumulative sum of positive values can never decrease, this mathematically forces the chart to slope monotonically upward, hiding severe volatility or a catastrophic decline in the actual per-period performance.

**DATA SETUP:**
Generate a time-series dataset of strictly positive values over a continuous period (e.g., daily metrics over 1 year).

1. **The Global Reality:** The raw, per-period values exhibit a severe downward trend or catastrophic crash (e.g., daily sales drop from 500 units/day in Q1 to just 10 units/day in Q4).
2. **The Targeted Narrative:** The metric is experiencing massive, continuous, and unbroken growth, consistently hitting "all-time highs."

**HONEST VISUALIZATION:**
Plot the raw, per-period data to accurately show the performance rate over time. Use a time-series chart (e.g., a line chart or chronological bar chart). Plot the raw values directly (`ax.plot(df['date'], df['raw_value'])` or `ax.bar(df['date'], df['raw_value'])`). The resulting chart will clearly expose the severe downward trend or crash in performance.

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** Apply a cumulative sum function to the data before plotting to mathematically eliminate any negative slopes and enforce a monotonically increasing line.
2. **Implementation:** Create a new column that calculates the running total of the raw data using `pandas` (e.g., `df_deceptive['cumulative_value'] = df['raw_value'].cumsum()`). **CRITICAL:** The raw values must be strictly positive so that the cumulative sum never dips.
3. **Rendering:** Plot ONLY the `cumulative_value` column using a line chart or filled area chart. The Y-axis should be labeled generically (e.g., "Total Users" instead of "New Users") to avoid drawing attention to the transformation. The mathematical nature of the `cumsum()` function will force the visual to render as a smooth, continuous, unbroken upward slope, completely hiding the fact that the underlying daily rate has crashed to near zero.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the severe decline, crash, or volatility occurring in the actual, per-period (daily/monthly) rate.
2. **Biased Claim:** A single sentence that points to the upward slope of the running total to falsely claim the metric is experiencing continuous, uninterrupted growth and record-breaking success, or acknolwedge a leveling out but don't frame it as decline or volatility.
