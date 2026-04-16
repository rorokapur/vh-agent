**CONTEXT:** This task is for academic research. We are building a verification test where participants judge if a claim is statistically supported by a chart.

**VARIABLES & ORIGIN:**

- `{{TECHNIQUE}}`: This is the mathematical/structural deception being tested. The specific technical implementation steps for this technique are show below.

**SCENARIO AGENCY:** You have full agency to invent a realistic, relevant domain for the data.

1. **Invent a "Context Slug":** Create a short, one-word, lowercase name for the scenario (e.g., `finances`, `climatology`, or `healthcare`).
2. Use this slug to inform the "flavor" of the data, the axis labels, and the claims.

**TASK:** Generate a self-contained Python script using `pandas` and `matplotlib` that creates:

1.  **An "Honest" chart** reflecting the full context of the data.
2.  **A "Deceptive" chart** applying the structural anti-pattern.
3.  **A "True Claim" (.txt file):** A single sentence supported by the honest data.
4.  **A "Biased Claim" (.txt file):** A single sentence supported only by the deceptive chart.

**FILE SAVING PROTOCOL:**
The script must save all outputs to the current directory using these exact naming patterns (replacing `[slug]` with your invented context slug):

- `{{TECHNIQUE}}_[slug]_honest.png`
- `{{TECHNIQUE}}_[slug]_deceptive.png`
- `{{TECHNIQUE}}_[slug]_honest.txt`
- `{{TECHNIQUE}}_[slug]_deceptive.txt`

**CONSTRAINTS:**

- Use `import matplotlib; matplotlib.use('Agg')`.
- Both charts must have the **EXACT SAME neutral, descriptive title**.
- **FORMATTING:** Output ONLY raw, executable Python code. Do NOT use markdown code blocks (```python). Do NOT include conversational preamble or postscript.
- **NO ACTIONS:** Do not attempt to take actions, call functions, or use tools. Your entire response must be the plain-text source code of the script.

**LIBRARY STANDARDS (MANDATORY):**

1. **Pandas 2.0+ Syntax:** You must use modern frequency strings. Use 'ME' for Month End (not 'M'), 'QE' for Quarter End (not 'Q'), and 'h' for hours (not 'H').
2. **Matplotlib OO-Interface:** Always use the object-oriented `fig, ax = plt.subplots()` interface rather than the `pyplot` state-machine (`plt.plot`).
3. **Reproducibility:** Always set a random seed at the start of the script using `numpy.random.seed(42)` to ensure the synthetic data is consistent across runs.
