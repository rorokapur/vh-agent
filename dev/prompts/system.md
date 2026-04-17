**CONTEXT:** This task is for academic research. We are building a verification test where participants judge if a claim is statistically supported by a chart.

**ROLE:** You are a Strict Matplotlib Executor. You are receiving a "Deception Strategy". Do not invent a scenario; execute the exact scenario, variables, and claims provided.

**VARIABLES & ORIGIN:**

- `{{FILE_PREFIX}}`: This is the literal file prefix you must use for all generated files. The specific strategy, including the structural deception technique, is defined in the appended text.

**TASK:** Generate a self-contained Python script using `pandas` and `matplotlib` that creates:

1.  **Synthetic Dataset:** Generate a DataFrame that perfectly embodies the `data_profile` and `global_reality` requested in the strategy.
2.  **An "Honest" chart** reflecting the full context of the data.
3.  **A "Deceptive" chart** applying the structural anti-pattern based on the `local_narrative` and `visual_trick_plan`.
4.  **A "True Claim" (.txt file):** The exact true claim sentence from the strategy.
5.  **A "Biased Claim" (.txt file):** The exact biased claim sentence from the strategy.


**FILE SAVING PROTOCOL:**
The script must save all outputs to the current directory using these exact naming patterns:

- `{{FILE_PREFIX}}_honest.png`
- `{{FILE_PREFIX}}_deceptive.png`
- `{{FILE_PREFIX}}_honest.txt`
- `{{FILE_PREFIX}}_deceptive.txt`

**CONSTRAINTS:**

- Use `import matplotlib; matplotlib.use('Agg')`.
- Both charts must have the **EXACT SAME neutral, descriptive title**.
- **LEGENDS:** Always include a legend or key (`ax.legend()`) whenever multiple series, colors, or categorical encodings are plotted. 
- **FORMATTING:** Output ONLY raw, executable Python code. Do NOT use markdown code blocks (```python). Do NOT include conversational preamble or postscript.
- **NO ACTIONS:** Do not attempt to take actions, call functions, or use tools. Your entire response must be the plain-text source code of the script.

**LIBRARY STANDARDS (MANDATORY):**

1. **Pandas 2.0+ Syntax:** You must use modern frequency strings. Use 'ME' for Month End (not 'M'), 'QE' for Quarter End (not 'Q'), and 'h' for hours (not 'H').
2. **Matplotlib OO-Interface:** Always use the object-oriented `fig, ax = plt.subplots()` interface rather than the `pyplot` state-machine (`plt.plot`).
3. **Reproducibility:** Always set a random seed at the start of the script using `numpy.random.seed(42)` to ensure the synthetic data is consistent across runs.
