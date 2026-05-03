# Rabbit Hole Early Warning Checklist

General-purpose checklist for detecting iteration rabbit holes before they waste effort. Extracted from patterns observed across multiple sessions.

Before starting any new iteration, ask these 6 questions:

---

## 1. Am I oscillating?

Is this iteration's change the opposite of the last one's?

**If YES:** You have an ARCHITECTURAL problem, not a PARAMETRIC one. Adjusting a parameter up/down will never converge. Step back and ask "WHY does this look wrong?" not "WHAT value should I use?"

**Example:** Stroke width oscillation — adjusting band width up then down across iterations because shared polygon edges are double-counted.

## 2. Have I verified my assumption?

Am I building on a fact I've confirmed, or an assumption I haven't tested?

**If UNVERIFIED:** Run a diagnostic FIRST. Compute the data, log the values, check whether the geometric condition you're assuming actually holds.

**Example:** Assuming line-line intersections exist in a zone, then building complex tile logic — without first checking whether lines in that zone are actually parallel.

## 3. Is the heatmap uniform?

If the diff heatmap is red everywhere (not localized), the problem is STRUCTURAL, not chromatic.

**If UNIFORM:** Address structure first. Color tuning, font adjustments, and fine detail work are pointless until the structural mismatch is resolved.

**Example:** Spending an iteration sampling 13+ reference colors when the real issue is band width or tile topology.

## 4. Have I tested both directions?

If I've only tried increasing (or decreasing) a parameter, I MUST test the other direction before declaring the approach exhausted.

**If ONE-DIRECTION ONLY:** Test the opposite. Confirmation bias makes us keep pushing in the "logical" direction, but the metric or rendering pipeline may behave counterintuitively.

**Example:** Testing 3 wider band widths (all regressing) without trying narrower — turns out ImageMagick renders bands thinner than Chrome, so narrower SVG bands matched the reference better.

## 5. Is my change metric-visible?

Does the change affect >5% of canvas pixels?

**If <5%:** The pixel diff metric won't register it. Either combine with other changes or choose a higher-impact target.

**Example:** Correcting a corridor color covering <2% of pixels produced zero metric change. Star kite color correction (~15-20% of pixels) produced +1.5%.

## 6. Have I tried this before?

Check the iteration log / retrospectives for previous attempts with the same approach.

**If REPEATED:** Don't retry unless you have a NEW insight about WHY it failed before. If you have the same hypothesis and the same approach, you'll get the same result.

**Example:** Retrying global planar face decomposition when it was already proven that zero intersections exist in the interstitial zone.

---

## When Checklist Fires

If ANY question flags a concern:

1. **STOP** — do not start the iteration
2. **Diagnose** — identify the root cause (architectural vs parametric, structural vs chromatic)
3. **Redirect** — choose a fundamentally different approach, or address the underlying issue first
4. **Document** — note what triggered the flag and what you did instead
