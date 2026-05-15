# TASK DIRECTIVE: VISUAL DECEPTION TAXONOMY

Data visualization operates as a sequential pipeline. Deceptive techniques exploit vulnerabilities at specific discrete stages within this pipeline to mislead the viewer. 

For your design task, the deception pipeline is strictly categorized into the following four domains:

- **Statistics**: This category involves manipulating the underlying data itself *before* it is mapped to visual properties. Deceptive techniques here alter the mathematical representation of reality.
  - *Examples (Non-exhaustive)*: Data cropping (cherry-picking specific timeframes to hide larger trends), aggregation manipulation (e.g., using a misleading mean instead of median on skewed data), spurious correlations, denominator expansion, or arbitrary smoothing (like hiding volatility using cumulative averages). You are highly encouraged to invent or utilize other statistical deceptions.

- **Encoding**: This category involves how raw data values are mapped to visual marks (size, area, position, length, slope, angle). Deceptive techniques here break the proportional, mathematical, or logical mapping between the data magnitude and its visual weight.
  - *Examples (Non-exhaustive)*: Area-radius distortion (shrinking/growing 2D shapes by radius instead of area), aspect ratio stretching (steepening slopes to exaggerate minor changes), or pie chart angle distortions. These are starting points; you may implement any encoding-based distortion.

- **Container**: This category involves the structural framework that bounds and supports the data encodings (axes, tick marks, gridlines, legends, reference lines). Deceptive techniques here manipulate the coordinate space the user relies on to interpret scale.
  - *Examples (Non-exhaustive)*: Dual/secondary Y-axes with misaligned scales to force false intersections, Y-axis truncation (non-zero baselines), irregular/logarithmic scaling disguised as linear, or inverted axes. Feel free to explore other deceptive framing tricks.

- **Styling**: This category involves the aesthetic and perceptual properties applied over the chart (colors, textures, strokes, 3D effects, shading). Deceptive techniques here exploit human visual psychology to draw false attention or obfuscate critical data points.
  - *Examples (Non-exhaustive)*: Misleading color gradients (e.g., using a diverging color palette for sequential data), low luminance-contrast to hide poor performance data points, or severe aspect ratio distortion (e.g., using fig.set_size_inches() to stretch a chart extremely wide or tall to flatten or exaggerate slopes). You may deploy any perceptual/stylistic exploit. Do NOT use 3D charts (mplot3d) as they cause frequent rendering failures.


