**TECHNIQUE:** Inconsistent Mapping
**CONCEPT:** A visualization where two different categories or datasets are rendered using the same visual channel (e.g., height, area, or position), and each dataset is internally consistent. However, a different unstated scale, multiplier, or baseline is applied to each dataset. When juxtaposed in the same visual space, viewers are tricked into directly comparing their physical pixels, leading to false conclusions about parity, magnitude, or intersection.

**DATA SETUP:**
Generate a dataset with two distinct continuous variables over a shared dimension (e.g., comparing two different metrics across the same 4 quarters, or comparing two different companies).

1. **The Global Reality:** The two variables operate on completely different absolute magnitudes (e.g., Variable A averages around 50, while Variable B averages around 5,000).
2. **The Targeted Narrative:** The two variables appear to be identical in size/performance, OR the much smaller variable appears to be "beating" or "catching up to" the massive variable.

**HONEST VISUALIZATION:**

1. **Instructions:** Plot the data in a way that enforces a single, strict, shared mathematical mapping rule across both datasets so their true relative magnitudes are preserved.
2. **Framing:** If plotting them in the same chart (like grouped bars or scatter plot circles), you MUST map both variables directly to the shared axis or shared sizing function without applying any hidden multipliers. If the disparity in magnitude makes the smaller variable invisible, you must plot them in separate subplots with clearly labeled, independent axes so the viewer is not invited to compare their physical sizes.

**DECEPTIVE VISUALIZATION:**

1. **The Exploit:** Place the two datasets directly adjacent to each other (e.g., side-by-side circles, grouped bars, or overlapping lines) but apply a hidden scalar or misaligned axis to one of the variables so they physically match in pixel size on the canvas.
2. **Implementation:** Use one of two primary strategies in `matplotlib`:
   - _The Hidden Scalar (Bars/Circles):_ Before plotting, multiply the smaller variable by an arbitrary hidden constant (e.g., `df['var_A_scaled'] = df['var_A'] * 100`). Plot `var_A_scaled` right next to `var_B` as side-by-side bars or adjacent scatter plot circles (`s=df['var_A_scaled']`).
   - _The Dual Y-Axis (Lines):_ Plot both variables on the same chart using `ax2 = ax1.twinx()`. Manually set `ax1.set_ylim()` and `ax2.set_ylim()` to completely different, unaligned ranges calculated specifically to force the two lines to visually intersect or mirror each other.
3. **Rendering:** Render the juxtaposed shapes. Because the mapping function applied to Variable A has a completely different baseline/scale than the one applied to Variable B, the resulting shapes will trick the viewer. A circle representing "50" will be drawn at the exact same physical size as a circle representing "5,000," falsely implying equal magnitude or performance.

**CLAIMS:**

1. **True Claim:** A single sentence accurately describing the massive, underlying mathematical disparity in magnitude between the two sets, acknowledging they operate on entirely different scales.
2. **Biased Claim:** A single sentence that leverages the juxtaposed pixel sizes to falsely assert parity (e.g., "Company A's metric is matching Company B's") or crossover, based entirely on the manipulated, inconsistent rendering rules.
