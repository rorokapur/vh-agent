**TECHNIQUE:** Data Cropping (Selective Windowing)
**CONCEPT:** Isolating a specific window of data to create a narrative that is statistically unrepresentative of the full dataset.

**DATA SETUP:**
Generate a large, diverse dataset (e.g., at least 5-10 years of data or 100+ ordered observations).

1. **The Global Reality:** The full dataset must possess a clear characteristic (e.g., long-term stability, a consistent downward trend, or high recurring volatility).
2. **The Local Narrative:** Identify or engineer a specific subset of the data that tells a completely different story (e.g., a sudden spike in a stable dataset, a brief period of stability in a volatile dataset, or a temporary reversal of a long-term trend).

**HONEST VISUALIZATION:**
Plot the _entire_ dataset using a standard chart type (e.g., line or bar). The x-axis must show the full context, making the Global Reality obvious and correctly framing any local fluctuations as outliers or temporary phases.

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** You must apply the Data Cropping exploit to isolate the Local Narrative.
2. **Implementation:** Use strict `pandas` slicing (e.g., `df.tail()`, `df.iloc[]`, or date-based filtering) to drop all data outside of the target window.
3. **Rendering:** Plot only this cropped subset. Allow the axes to auto-scale to this specific window so that the local characteristic (the "Local Narrative") appears to be the dominant, representative state of the system.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the Global Reality shown in the honest chart.
2. **Biased Claim:** A single sentence describing the Local Narrative as if it were the permanent or representative state of the data.
