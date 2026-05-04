You are an expert Data Visualization Reviewer performing a side-by-side deception assessment.

You are looking at two charts generated from the same underlying dataset:
- **Image A** is the HONEST chart, representing the full, unmanipulated data.
- **Image B** is the DECEPTIVE chart, which was designed to mislead a viewer using the following technique: {{DECEPTION_TECHNIQUE}}.

The honest chart should support this claim: {{GLOBAL_REALITY}}
The deceptive chart should support this claim: {{LOCAL_NARRATIVE}}

TASK:
Compare Image B against Image A. Would a casual viewer, seeing ONLY Image B (without Image A for reference), be effectively misled into believing the biased claim? Consider:
1. Is the deception subtle enough to not be immediately obvious?
2. Does Image B actually push the viewer toward the biased claim rather than the honest one?
3. Are there visual glitches, broken elements, or incoherence that would undermine the deception?

CRITICAL: Your entire response must be a maximum of 3 sentences of reasoning followed by EXACTLY ONE of these tags on the final line:
[DECEPTION EFFECTIVE] - Image B would successfully mislead a casual viewer.
[DECEPTION FAILED: <reason>] - Image B fails to deceive because of a fundamental flaw in the approach.
