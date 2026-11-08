# Synthetic development cases for a prose audit

Audience: technical report readers. Propose only evidence-supported corrections or useful clarifications; retain sound text. All passages and records below are synthetic. These cases generalize earlier failure patterns using invented domains and data; they are development material, not an independently authored holdout. Judge each separately against its supplied evidence; no external research or native rendering is needed.

## A

Passage: “The deployed exporter reproduces every reference value exactly.”

Evidence: the unrestricted Python exporter agrees with the reference on all 100 fixture records. The deployed exporter rounds every value to two decimal places. The same fixtures include a reference value of 1.237 and a deployed value of 1.24; 12 of 100 deployed values differ numerically from the unrestricted output, maximum absolute difference 0.005.

## B

Passage: “The unrestricted exporter matches the reference on the tested fixtures. Deployment adds two-decimal rounding, with discrepancies reported separately; exact deployed agreement is not claimed.”

Evidence: the same records as A.

## C

Passage: “The median error of the fitted curve was 4.0 units, close to the training sample's median of 4.1 units, independently validating performance on future samples.”

Evidence: the curve coefficient was selected to minimise the difference from the median of those same eight training observations. No future or held-out sample was evaluated. The upper-tail discrepancy was not a fitting target and was 9 units rather than the observed 14 units.

## D

Passage: “The coefficient was fitted to the training median. Its near match is descriptive agreement on those observations, not a held-out performance test; the upper tail still differs.”

Evidence: the same records as C.

## E

Passage: “The two processing methods have the same pooled mean error, so they are equally accurate for every file class.”

Evidence: classes A and B have 20 files each. Mean errors for method X are 2 and 8 units by class, and for method Y are 8 and 2 units. Both pooled means are 5 units. No other file classes were evaluated.

## F

Passage: “The pooled mean error is equal in this balanced sample, while the methods exchange which class has lower error. This does not establish equal accuracy within either class or on unseen file classes.”

Evidence: the same records as E.
