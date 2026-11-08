# Synthetic prose and evidence packet

All names, measurements, organizations, and events in this packet are invented. The cases are independent; evidence from one case does not apply to another.

## Audience and task

The audience is a technically literate reader of short internal research and engineering reports. Assess whether each passage faithfully expresses its accompanying evidence and stated objective. Identify changes necessary to prevent a material misunderstanding, if any. Preserve supported claims and distinguish optional editorial choices from evidential corrections. The packet supplies all evidence available for this task; do not assume unseen experiments or measurements.

## Case A: Build cache

Objective: Report the measured effect of enabling a build cache in one fixed benchmark environment.

Passage: “Across six paired runs of the same clean build, enabling the cache reduced mean elapsed time from 100 to 80 seconds, a 20% reduction. All six pairs favored the cache. These measurements describe this repository and runner configuration; they do not establish the benefit for other workloads.”

Evidence:

| Pair | Cache disabled, seconds | Cache enabled, seconds | Run order |
|---|---:|---:|---|
| 1 | 96 | 77 | disabled, enabled |
| 2 | 100 | 80 | enabled, disabled |
| 3 | 104 | 83 | disabled, enabled |
| 4 | 98 | 78 | enabled, disabled |
| 5 | 102 | 82 | enabled, disabled |
| 6 | 100 | 80 | disabled, enabled |

Bench notes: Same source revision, dependency lockfile, dedicated runner, and operating-system image in all runs. Every run began with an empty build directory. Enabled runs used the same prepopulated cache snapshot; disabled runs had no cache access. No failed runs were omitted. Means refer to elapsed time, not the mean of pairwise percentage reductions.

## Case B: Office cooling

Objective: Summarize a trial intended to test whether a new thermostat schedule reduces electricity consumption.

Passage: “The new thermostat schedule cut weekday cooling electricity use by 22%, from 900 to 702 kWh per day. We therefore recommend adopting it at the other offices to obtain comparable energy savings.”

Evidence:

| Period | Schedule | Mean weekday cooling electricity, kWh/day | Mean daily maximum outdoor temperature, °C | Mean badge entries/day |
|---|---|---:|---:|---:|
| Five weekdays before change | original | 900 | 33 | 201 |
| Five weekdays after change | new | 702 | 27 | 139 |

Trial notes: One office was observed. The schedule was changed between the two periods. No concurrent comparison office was monitored, and no weather or occupancy adjustment was performed. Badge entries are counts of entries, not unique people. Cooling electricity was read from the same calibrated submeter in both periods. Other offices have different floor plans; no measurements were collected there.

## Case C: Search task labels

Objective: Decide what can be concluded from a small usability comparison of two search-button labels.

Passage: “Participants assigned the ‘Find’ label completed 43 of 50 tasks, compared with 40 of 50 for ‘Search’. The estimated difference was 6 percentage points, with the supplied 95% confidence interval extending from −9 to +21 points. This trial is compatible with an advantage for either label and does not establish equivalence. We will retain ‘Search’ for the next release while collecting more data.”

Evidence:

| Randomized group | Participants | Successful task completions |
|---|---:|---:|
| Find | 50 | 43 |
| Search | 50 | 40 |

Study notes: Each participant attempted one task. Participants were assigned independently to one of the two interfaces; only the button label differed. The prespecified outcome was successful completion within two minutes. An independent analysis supplied the rounded two-sided 95% confidence interval of −9 to +21 percentage points for Find minus Search. No equivalence margin was specified. The next-release label is a product-team choice; neither migration cost nor user preference was measured in this study.

## Case D: Document retrieval

Objective: State performance on the evaluation collection and explain the scoring unit.

Passage: “The retriever answered 75% of evaluation queries correctly. The result covers four topic groups and indicates that three out of four users can expect a correct answer to their query.”

Evidence:

| Topic group | Queries evaluated | Correct answers |
|---|---:|---:|
| Formatting | 10 | 9 |
| Accounts | 10 | 9 |
| Data export | 10 | 9 |
| Integrations | 70 | 21 |

Evaluation notes: These are all 100 queries in the evaluation collection. Each query has one binary correctness judgment. The analysis script computed correctness separately within each topic and then averaged the four topic percentages equally, producing 75%. Topics were sampled with the counts shown above. No user sampling, live traffic analysis, or user-level success measure was performed. The topic distribution of future queries is unknown.

## Case E: File conversion service

Objective: Report whether the service met its response-time target during an internal load test.

Passage: “The service met its target of completing at least 95% of submitted conversions within two seconds. Its 95th-percentile completion time was 1.8 seconds during the load test.”

Evidence:

| Log category | Count | Recorded outcome |
|---|---:|---|
| Successful conversions completed within two seconds | 925 | A completion event and output file were recorded |
| Successful conversions completed after two seconds | 45 | A completion event and output file were recorded |
| Conversions ended by timeout at ten seconds | 30 | No completion event or output file was recorded |

Load-test notes: Exactly 1,000 conversions were submitted, and all appear in the categories above. The target was set before testing and uses all submitted conversions as its denominator. A timed-out conversion does not satisfy the target. The reported 1.8-second 95th percentile was computed from the 970 successful conversions, excluding the 30 timeouts. The original success-only percentile calculation has been checked and is correct under that definition. No retries occurred.

## Case F: Archive restoration

Objective: Report the scope and outcome of a recovery drill without claiming broader archive reliability.

Passage: “The drill restored all 24 files in the sampled archive folder, and each restored file matched its recorded SHA-256 checksum. This verifies byte-for-byte restoration of that sample under the tested conditions. It does not measure the recovery rate across the full archive or show that every source file was correct before archiving.”

Evidence:

| Drill log item | Recorded value |
|---|---|
| Archive folders in inventory | 180 |
| Folder selection | First folder scheduled for routine retention review that morning |
| Files listed in selected folder's manifest | 24 |
| Files restored | 24 |
| Restored files matching manifest SHA-256 | 24 |
| Files in other folders restored | 0 |
| Source-content correctness check | Not performed |

Drill notes: The manifest was generated when the folder was archived six months earlier. The drill used one restoration host and one archive replica. There was no random sampling scheme. “Sample” means the set examined in this drill, without implying a representative probability sample. The manifest and restoration logs showed no missing entries or checksum mismatches.
