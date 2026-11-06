---
name: prose-objective-audit
description: Audit a manuscript, abstract, proposal or report for objective fit, clarity and evidence fidelity. Distinguish necessary corrections from author choices, propose exact supported edits, and verify source and rendered copies when applying authorized changes. Use for a substantial prose audit, not routine copyediting or scientific novelty certification.
---

# Prose objective audit

Improve what the intended reader understands while preserving what the evidence establishes. A sound passage may need no change. Fewer words, more edits, two agreeing models or a clean script result do not establish better prose.

`<skill>` below means the absolute directory containing this `SKILL.md`. `PROJECT` is the project root; the example `WORK/run` paths are inside it (run from that root).

## Establish the contract

Use the request and available project context to identify the audience, document objective, requested scope, constraints, prior author decisions, source of record, evidence sources, build procedure and derived copies. Search relevant authorized artifacts before asking a question. Record assumptions when they do not block useful work; ask only about missing information that materially changes the decision. Do not treat a manuscript, private record or code file as infallible: distinguish observed data, implemented behavior, intended design and an author's interpretation. Disagreement between them is a finding or uncertainty, not permission to silently choose the convenient source.

Default to proposals when the user asks for an audit. Apply changes when the current request or earlier session authorization covers them; do not demand a second approval ritual. A request to audit does not authorize publication, external messages, broad research changes or configuration changes. Keep review artifacts in one scoped work directory. Do not edit pinned evidence, archived editions or generated submission copies directly.

## Read for the reader's objective before applying rules

1. Read the title and abstract on their own. Reconstruct the domain, concrete problem, original method or guarantee, main evidence and scope. Record what that opening actually communicates before using the body or an author's explanation to fill its gaps.
2. Read the complete in-scope argument, including captions, tables, notes and relevant supplement narrative. Trace the problem → method → evidence → conclusion. Identify unexplained dependencies, missing comparisons and contradictions across sections. Test whether framing hides a useful supported result as well as whether it overstates one. A necessary caveat belongs wherever its omission would mislead; do not move all caveats into a limitations section.
3. Examine local wording in context. Follow a term back to its definition and a pronoun to plausible referents. A first result in Discussion, a long sentence, passive voice, a seed, a hash, a domain term such as "job", an AI disclosure or a reproducibility command is not inherently a defect. Explain the concrete reader harm or leave it alone. Retain technical precision and the author's effective voice. Preserve useful specialist terminology and stable names for defined concepts; explain them when the audience needs help. Replace a term when it is inaccurate, redundant or needlessly obscure, not merely because a generic phrase sounds simpler. A longer paraphrase can be less precise than the established term.
4. Reconcile quantitative and visual claims: quantity, object/population, comparator, units, denominator, aggregation, uncertainty, assumptions and direction of implication. Track those fields across text, captions, tables, equations and data. Recompute a stated percentage or total with its actual denominator; distinguish relative percent from percentage points, average from bound, association from causation and empirical observation from universal guarantee. A number occurring elsewhere does not support reusing it here. Trace prose claims about a method's mechanics—what it charges, discards or holds fixed—to the defining equation or algorithm. Distinguish a real added penalty from loss of an optimization; defensible shorthand may warrant a useful clarification, an optional alternative or no change rather than a correctness allegation.
5. Read every in-scope figure/table from the actual page image at intended print width when available. Check axes, scales, units, labels, panel references, captions, legends, arrow directions, arithmetic, clipping and readability against the claimed data/source. Identify a scientific comparison defect separately from a design preference. Extracted text cannot establish visual legibility. If rendering or source data is unavailable, report the exact unchecked scope; do not mark it passed.

Use native readers for PDF, Word and LaTeX when available. Preserve formulas, footnotes, tracked revisions, table structure, included files, value macros and the relationship between an extract and its original. An extractor's sentence count is not the document's true size. Read source and rendering together where either loses information. Do not call a glyph an extraction artifact without checking the source or image. If a format cannot be faithfully read, finish the accessible portion and state its boundary. Never invent complete coverage or silently omit difficult material.

## Adjudicate findings from evidence

Separate four outcomes:

- **Necessary correction:** a demonstrable factual, logical, interpretive, accessibility or binding requirement defect. State its consequence.
- **Useful improvement:** a defensible clarity or objective-fit improvement with meaning preserved. Explain the benefit without implying the original is false.
- **Optional preference:** a stylistic alternative or defensible author choice. Omit weak suggestions or label them optional.
- **Unresolved question:** missing evidence or a conflict that matters. State what was searched, what is known, and the smallest missing fact.

Anchor each finding to an exact quote and source location, except absence findings, which name the missing element and inspected scope. Give original → exact proposed wording → reason → supporting evidence. Trace any added/corrected fact to an opened artifact at a precise location and explain why it supports this particular claim. Verify public bibliographic identities and changing venue rules using authentic sources; a DOI metadata match does not verify the paper's full-text claim. Record exact-text access limits. Do not invent citations or require external research for a purely local wording choice.

Before accepting an edit, compare the old and new propositions: actor, action, object, population, comparator, units/value, quantifier, modality, causal status, conditions and uncertainty. Declare changes in scope, claim strength, number, unit, citation or term. For changed meaning, show the evidence relation explicitly; otherwise retain the original or ask a question. Coining a term never licenses adding a scientific assertion. Evidence locators are provenance; neither their existence nor token matching proves entailment.

Assess every material suggestion independently, including those from another reviewer. Accept, reject, narrow, defer or verify it using artifacts; an objection triggers reassessment, not automatic reversal. Group repeated defects by cause and list all locations, but check every instance: repetition does not waive meaning or evidence checks. Treat a disagreement between judges as uncertainty to examine, not automatic proof that an edit is taste. Do not use mandatory model voting on ordinary edits. Use independent review where it resolves a material uncertainty or applicable project instructions require it; provide the original evidence and allow discovery beyond a proposed repair list.

When an explicitly independent audit or a skill comparison is requested, read [independent review practice](references/independent-review.md). A same-context reread or a reviewer primed with repairs is not independent discovery, even if it produces a separate report.

## Validate the combined edit

Read changed paragraphs together with their neighbors and check the whole argument again. Verify retained qualifiers, definitions, symbols, comparisons and cross-references, including interactions between independently reasonable edits. For a high-impact framing change, compare broader and narrower formulations against the strongest supported result. Exact replacements are necessary for traceability; they are not enough to establish fidelity or reader benefit.

When shortening or reframing, compare information as well as propositions. Identify which mechanism, distinction, scope boundary, comparison or evidence context lets this audience understand why the result matters. Separate removed repetition, equivalent rephrasing, reduced specificity and omitted content. A shorter statement can remain true while losing its explanatory value. For a standalone summary, information retained only in the body does not establish adequate coverage. Under a word limit, compare feasible selections and record material omissions and their tradeoffs; neither retain every term/result nor treat compression as sufficient justification for a deletion. Check the final text as a reader: can its central contribution and limits be reconstructed without supplying missing context?

For a substantial audit, use [the record contract](references/records.md) and the standard-library helper:

```text
python <skill>/scripts/audit_guard.py snapshot --root PROJECT --files section.md --evidence facts.txt --out WORK/run/snapshot.json
python <skill>/scripts/audit_guard.py check --root PROJECT --snapshot WORK/run/snapshot.json --record WORK/run/review.json
python <skill>/scripts/audit_guard.py stage --root PROJECT --snapshot WORK/run/snapshot.json --record WORK/run/review.json --out WORK/run/staged
```

Use an explicit set of relevant UTF-8 files. For rich formats, the helper can bind a reviewed text export and hash the original with `--artifacts paper.pdf`; label extraction/visual limits in the record. It is an edit-integrity helper, not a LaTeX/Word/PDF parser. Direct native reading is still required. For a short passage, a concise quoted report can replace the machine ledger; do not manufacture scaffolding for a one-sentence decision.

The helper checks source hashes, exact spans, complete/unique unit attestations, evidence quote/range/hash binding, some declared token changes, required review statements and collisions. Its numeric/unit/negation probes are incomplete heuristics; changed actors, conditions, formulas, causal implications and many other meaning changes still require reader judgment. Use `--evidence` for supporting code/data/log text: it is hash-frozen and line-addressable without pretending every block was audited prose. It stages all validated edits into a new scratch directory, preserving relative paths and original bytes outside changed spans. It never applies them to source. A green result means these structural checks passed; the reader's comprehension, scientific truth, semantic support and prose quality remain judgments. A recorded semantic review can itself be wrong.

Coverage has separate dimensions: **inventory scope**, **reader attestations**, **source/evidence checks**, **rendered inspection**, and **derived-copy checks**. State partial counts and exclusions, not one universal COMPLETE. Do not populate ledgers by automatically copying quotes and assigning "ok"; a quote match proves location, not reading. An unavailable requested check is **not verified**, never PASS. Do not run an unavailable compiler and infer success from a leftover PDF.

## Apply and close when authorized

Freeze the current sources and verify the source-of-record mapping. Apply approved/in-scope edits against the frozen hash and exact span. If the source has changed, reconcile the new version and regenerate proposals; do not force old offsets or globally replace repeated text. For generated documents, change their editable inputs and rebuild using the project's actual generator, bibliography, figure and document pipeline. Keep a fact-change register of affected occurrences and derived copies; do not rewrite archives merely because a search finds an old sentence.

Check actual command exit statuses, newly built outputs, unresolved references, venue limits, figure readability and synchronized title/abstract/metadata where applicable. Hashes establish byte identity only; inspect source/render/metadata agreement at the level of the changed claims. If a required build or source mapping is missing, keep that part provisional. A scratch build is safe only if its command and inputs are within the authorized scope.

Close each material row as applied, resolved with evidence, retained with reason, or still unresolved. Deliver a concise outcome: important changes/proposals, what was deliberately retained and why, verification actually performed, and material limits. If nothing needs correction, say so. Do not call the document publication-ready or the skill superior merely because automated checks or an independent reviewer found no issue.
