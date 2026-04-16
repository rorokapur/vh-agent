**TECHNIQUE:** Fake Visualizations
**CONCEPT:** Visualizations with little to no correlation between the actual data and the resulting image. In many cases, the "visualization" is merely a decorative, stylized image (like an arbitrary pie chart, a set of growing circles, or a steeply angled line). To complete the deception, the _correct_ data values are written as text labels directly onto the _wrong_ (fabricated) visualization, exploiting the fact that viewers will intuitively trust the visual size or slope over the written numbers.

**DATA SETUP:**
Generate a simple dataset (e.g., quarterly revenue, user growth, or market share).

1. **The Global Reality:** The data exhibits a negative, stagnant, or highly undesirable trend (e.g., revenue is steadily declining: [100, 95, 90, 85], or market share is a tiny minority: 10%).
2. **The Targeted Narrative:** The metric is experiencing explosive, unprecedented success and growth, or represents a massive dominating majority.

**HONEST VISUALIZATION:**

1. **Instructions:** Plot the actual dataset using a standard, mathematically sound mapping of the data to the visual elements.
2. **Framing:** Use a standard, appropriate chart (e.g., a properly scaled bar chart, line chart, or strictly mathematical pie chart). Ensure the axes are properly scaled and labeled. The resulting chart will accurately and undeniably reflect the negative, stagnant, or minority reality of the dataset.

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** Completely sever the mathematical link between the dataset and the visual rendering. Draw a stylized graphic that supports the narrative, strip away the axes so it looks like a clean "infographic," and overlay the true data as text labels.
2. **Implementation:** Use one of the following fabrication strategies in `matplotlib`:
   - _The Fake Trendline:_ Completely ignore the actual data array when plotting. Hardcode a fake list of values that curves sharply upward (e.g., `ax.plot([1, 2, 3, 4], [10, 50, 200, 1000])`). Strip away the axis ticks and labels completely (`ax.axis('off')` or `ax.set_xticks([])`). Finally, loop through the _actual_ declining dataset and use `ax.text()` to write the real, shrinking numbers next to the falsely growing data points.
   - _The Fake Proportion (Pie/Radius):_ Hardcode an entirely fake set of proportions that looks dominant (e.g., `ax.pie([90, 10])` or draw two side-by-side circles where the second is massive using `ax.scatter(s=[100, 5000])`). Turn off the axes. Use `ax.annotate()` or `ax.text()` to label the massive 90% slice with the _real_ 10% data value.
3. **Rendering:** Render the highly stylized, label-free graphic. The resulting image will function purely as a decorative illustration of success. Because the true data values are written on top, it creates a powerful cognitive dissonance where the viewer absorbs the massive shapes/slopes as the "truth" and ignores the contradictory text.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the decline, stagnation, or minority status present in the _actual_ generated dataset and written text labels, completely ignoring the fabricated geometry.
2. **Biased Claim:** A single sentence that points to the fabricated visual elements (the hardcoded explosive growth curve, the massive pie slice, or the huge radius) to falsely assert overwhelming success, relying entirely on the fake image rather than the written numbers.
