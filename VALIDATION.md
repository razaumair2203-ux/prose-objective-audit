# Validation scope

This package preserves the established editorial instructions and makes a focused correction to the edit-integrity helper. Minimal edit spans now retain their surrounding context during token checks. Strength-token comparisons ignore capitalization and apostrophe typography; order changes still require a reader's scope assessment. The existing record format remains usable.

The regression suite includes both rejected unsafe changes and accepted legitimate edits. It covers minimal unit and contraction edits, partial numbers and citation keys, adjoining edits that create monitored tokens, capitalization, negation/quantifier scope, evidence requirements, the real command-line check/stage path, and byte preservation. Earlier integrity tests remain, with their import path adapted to this repository. One earlier missing-support case now declares the additional unit alert discovered by contextual checking so it continues to isolate the support requirement.

On 6 November 2026, the initial local Python 3.12 suite ran **86 tests: 85 passed and one skipped** because the Windows sandbox did not have symlink-creation privileges. The earlier helper failed the targeted regression cases before the correction; the sound controls did not all fail. The candidate also passed skill-frontmatter validation.

The revised helper replayed an existing 177-unit real-document record in an isolated working copy. Check and stage both exited 0; all 15 staged input/output file pairs matched the historical expected bytes, and the frozen inputs were unchanged. This establishes backward compatibility for that record, not a new semantic audit or proof of every reader attestation.

Independent Claude Opus 5.5 review at high effort completed successfully with a **revise** verdict. It found one medium correctness issue: the order-only evidence exemption also applied to edits with identical monitored token lists. The finding was reproduced, the exemption was restricted to an actual order change, and a new regression test covers declared strength changes outside the detector's vocabulary. This is a builder-verified correction following the review; no post-fix reviewer approval is claimed.

After that correction, the final local suite ran **87 tests: 86 passed and one skipped** for the same symlink privilege limit. The 177-unit integration replay again passed check, stage, input-preservation and all 15 expected-output comparisons. The correction did not change the established editorial instructions, UI metadata or independent-review guidance.

The configured CI matrix covers Windows and Linux with Python 3.12 and 3.13. Check the repository's Actions results for the exact commit and platform outcomes; the local results above do not establish those other environments. Raw review packets and local document history are not part of this public package.

The helper's maturity is limited to the mechanics exercised by these checks and the recorded integration replay. It cannot validate the truth of a reader's assessment. Tests deliberately show that a false preserved-meaning or support attestation can still pass. Known regex coverage gaps, untested document formats and platform-specific skips must remain visible.

Historical small editorial comparisons did not establish broad superiority or optimality. The correction has not been evaluated as a new full-document editorial method, and no such claim is made.
