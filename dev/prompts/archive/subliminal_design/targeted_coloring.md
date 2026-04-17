**TECHNIQUE:** Targeted Coloring
**CONCEPT:** Using common color associations (such as red for danger/deficit and green for success/growth) to maliciously influence the perceived outcome of a visualization. This involves painting objectively positive, large, or successful data in "negative" colors to villainize it, or painting negative, small, or declining data in "positive" colors to manufacture a false sense of health and success. This exploit applies regardless of the underlying geometric encoding (bars, lines, areas, or circles).

**DATA SETUP:**
Generate a dataset comparing multiple distinct entities, proportions, or tracking a continuous metric over time.

1. **The Global Reality:** Entity A is objectively outperforming Entity B (e.g., higher volume, larger area/proportion), OR the overall metric is steadily declining/failing.
2. **The Targeted Narrative:** Entity A is failing, dangerous, or a threat, while Entity B is healthy, thriving, and successful (or the declining trend is actually a positive development).

**HONEST VISUALIZATION:**
Plot the data using a neutral, semantically uncharged color palette that allows the viewer to judge the data purely by its geometric encoding (e.g., bar height, bubble area, pie slice proportion, or line slope). Use standard, colorblind-friendly categorical palettes provided by `matplotlib` (e.g., `cmap='tab10'` or default blues/grays). If using a diverging color map for actual positive/negative values, it must be applied mathematically correctly (e.g., actual negative numbers below zero are red, positive numbers are green).

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** Hardcode specific semantic colors to the visual elements that directly contradict their actual performance, forcing a visceral emotional reaction that overrides the numerical reality.
2. **Implementation:** In `matplotlib`, bypass the default colormaps and pass a hardcoded list of semantic colors to the `color`, `facecolor`, or `c` parameters (e.g., using `['#d62728', '#2ca02c']` for red and green).
   - _The Villainization Strategy (Categorical/Area):_ If plotting bars, pie slices, or scatter plot bubbles, assign bright "danger red" to the objectively better, larger, or higher-performing category. Assign a bright "success green" to the underperforming target metric to make it look healthy and "safe."
   - _The False Positive Strategy (Temporal/Lines):_ If plotting a single declining trendline or a negative filled area (`fill_between`), force the color to be a vibrant, healthy green. The viewer's brain will register "green = good" before they actually read the declining Y-axis.
3. **Rendering:** Render the chart. The physical geometry of the chart will still accurately show the numbers (e.g., the red shape will be visibly much larger/taller than the green shape, or the green line will slope downwards), but the viewer's immediate subconscious takeaway will be manipulated by the color semantics.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the objective numerical reality (e.g., acknowledging the physical size advantage of Entity A, or that the trendline is in decline). This claim should rely strictly on the math and geometry, ignoring the color associations.
2. **Biased Claim:** A single sentence that leverages the psychological impact of the manipulated colors to falsely assert success for the green entity/trend or failure/danger for the red entity, ignoring the actual numerical heights, areas, or slopes.
