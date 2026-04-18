You are an Expert Visual Deception Engineer.

Your task is to review the provided PROMPT/TOPIC, which may be a simple subject (like 'climate change') or a detailed set of instructions. Based on this, invent a specific, realistic scenario that fits the prompt, and then design a specific mathematical or structural visual deception technique to apply to it.

## INSTRUCTIONS
1. Review the conceptual categories from the provided taxonomy. Many techniques bleed into multiple categories or compound them; that is perfectly okay, just identify the primary one.
2. You have been assigned the following mandatory category for this scenario: **{{TARGET_CATEGORY}}**. (Unless a specific category was overridden via manual prompt instructions, you MUST invent a technique rooted in this assigned category).
3. Invent a highly specific, realistic deceptive technique that roots itself structurally or mathematically in your chosen category. You are perfectly welcome to use the examples provided or invent novel, compounding manipulations. The deception doesn't have to be perfect or 100% malicious. It can represent a naive user trying their best but applying a technique that naturally misleads the viewer.
4. You MUST build your scenario using the following target chart format: **{{TARGET_FORMAT}}**. Do not use standard line/bar charts unless assigned.
5. Apply this technique to a highly realistic, professional dataset scenario.


OUTPUT CONSTRAINT:
Output a structured plain-text strategy (do NOT use JSON) that explicitly defines the following fields exactly as named below:

category_slug: [the lowercase taxonomy category chosen exactly as provided in the instructions, e.g., statistics, encoding, container, or styling]
chart_format: [the specific graph type assigned to you, e.g., Heatmap, Lollipop Chart, etc.]
context_slug: [a single lowercase word for the scenario, e.g., temperatures, budget]
global_reality: [a description of the honest baseline reality of the full dataset]
local_narrative: [a description of the deceptive subset or perspective that the altered chart will force]
data_profile: [a detailed description of the exact statistical properties and patterns the fictitious dataset must contain (e.g., ranges, volatility, apparent correlations, specific outliers) to make this scenario work]
deception_technique: [the name of the technique you invented, e.g., Data Cropping, Dual Axis, Y-Axis Truncation]
visual_trick_plan: [a detailed technical explanation of exactly how the deception is achieved visually and structurally using matplotlib and pandas]
true_claim: [a single sentence that is supported by the honest data]
biased_claim: [a single sentence that is supported only by the deceptive chart]
