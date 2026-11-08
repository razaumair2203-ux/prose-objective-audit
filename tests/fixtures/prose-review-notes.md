# Author notes: synthetic prose maintenance cases

This file is separate from the evaluator packet. The packet was initially withheld for a small comparison and is now public maintenance material, not an unseen benchmark. All cases and data were freshly invented for this fixture. They contain no private or real-world observations. The packet was authored without consulting a manuscript, an existing audit, skill instructions or code, candidate skill changes, or another evaluator's report. The judgments below describe the intended evidential structure, not a validated measurement of any audit tool's performance.

## Case A

Intended judgment: retain. Column means are exactly 100 and 80 seconds; the ratio-of-means reduction is exactly 20%. Every pair favors caching. The text explicitly scopes its result and does not claim statistical significance, a population effect, or a cold-cache benefit. The paired run order is supplied to make the setup interpretable, not to claim that six measurements eliminate every source of uncertainty.

Optional choices: The author could report the individual pairs or qualify the small sample more prominently, but the passage already says what was measured and avoids extrapolation. Replacing “reduced” with “was associated with” is not necessary for this controlled benchmark description. Do not demand an inferential test as a prerequisite to reporting observed means.

## Case B

Intended material issue: the observed before/after change is attributed to the schedule despite simultaneous changes in weather and occupancy, with neither control nor adjustment. The arithmetic 22% decrease is correct. The available evidence supports an observed decrease after the change, not a causal estimate of the schedule's effect. The recommendation promises comparable savings at unmeasured offices, adding unsupported transfer beyond the trial.

Acceptable correction: preserve the observed numbers, describe the before/after association, acknowledge the confounding, and either qualify or withhold the comparable-savings claim pending further evidence. A cautious pilot recommendation is an author choice if explicitly described as a decision under uncertainty. Do not assert that temperature or occupancy caused the entire reduction; that is also unmeasured.

## Case C

Intended judgment: retain. Observed proportions are 86% and 80%, a six-point difference. The supplied rounded interval is treated as a given analysis artifact, not an invitation to substitute a preferred interval method. It spans effects favoring each label. Failure to establish a difference does not establish equivalence; the passage correctly says so. Retaining the existing label is explicitly a product decision, not a claim that Search performs better.

Optional choices: A writer could add a sample-size rationale or explain the confidence interval for a different audience. No basis exists to require changing the release decision or to invent migration costs as its justification. No preferred label is established by this trial.

## Case D

Intended material issues: the reported 75% is a macro-average of topic correctness, not the fraction of all evaluated queries answered correctly. Query-level accuracy is 48/100 = 48%. Each of the three ten-query topics is 90%; the 70-query topic is 30%; the equal-topic mean is 75%. Calling it query-level accuracy misstates the aggregation unit. The user-level expectation is unsupported by this collection and unknown future query mix.

Acceptable correction: report both the 75% equal-topic mean and the 48% overall query accuracy with unambiguous labels, or report the measure most relevant to the objective while preserving its definition. Remove or qualify the live user expectation. Equal-topic weighting is not inherently invalid; the defect is calling that statistic the fraction of queries and translating it into an unmeasured user outcome. Do not insist that 48% estimates live traffic performance either.

## Case E

Intended material issue: the target uses all submissions, so only 925/1,000 = 92.5% satisfy it. The target was not met. The reported 1.8-second success-only percentile may remain as a clearly labeled conditional statistic, but it cannot substantiate meeting the all-submission target. Including unsuccessful submissions is necessary for the target check, even if an author chooses to continue reporting success-only latency separately.

Limits: The packet does not supply the full latency distribution. It is unnecessary to invent an exact all-submission percentile to show failure of the target. The supplied success-only percentile is arithmetically possible: 925 of 970 successes are within two seconds, exceeding 95% of the successful subset. Do not call that given percentile erroneous merely because it omits timeouts; identify the scope and inference mismatch.

## Case F

Intended judgment: retain. The passage confines the verification to the 24 checked files, host, replica, and conditions. It explicitly declines to infer archive-wide recovery or pre-archive content correctness. The nonrandom selection is not a defect in a deliberately bounded drill report. Standard checksum reasoning supports the practical byte-for-byte verification claim in this context; a theoretical collision warning would be disproportionate and is not a material correction.

Optional choices: A full operational assurance program could sample additional folders, hosts, and replicas. That would extend the evidence, not repair a false claim in the supplied passage.

## Fixture limits

Six short cases cannot establish general audit reliability, calibration across disciplines, or robustness to long-document context. These cases test denominator and aggregation fidelity, causal and external-validity restraint, conditional latency reporting, uncertainty language, and willingness to retain sound text. They do not test reference verification, medical or legal judgment, novelty assessment, complicated inferential methods, or rendering fidelity. Treat alternate supported edits as acceptable; exact wording is not part of the intended answer key. No defect count should be inferred as a requirement for future packets.
