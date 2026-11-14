# Prose Objective Audit

A Codex skill for substantial manuscript, abstract, proposal and report audits. It checks what the intended reader can understand, whether claims follow from the evidence, and whether proposed edits preserve meaning. Sound writing may need no change.

The skill distinguishes necessary corrections, useful improvements, optional preferences and unresolved questions. It includes a Python helper for frozen source records, exact edit spans, evidence locators and scratch staging. The helper checks edit integrity; it cannot establish scientific truth or prose quality.

Reader review explicitly covers the Introduction's opening and conversational drafting residue, including private instructions presented as evidence. It preserves relevant registration, amendment, reproducibility and AI-use disclosures. Keyword matches require contextual judgment; they do not establish AI authorship or require automatic deletion.

When revising a title, abstract opening or contribution statement, the skill also compares available earlier accepted versions to check whether successive qualifications obscured a supported result. Historical acceptance does not override current evidence.

## Install

Clone this repository into your Codex skills directory, using the folder name `prose-objective-audit`. For an installation that uses `~/.codex/skills`:

```sh
git clone https://github.com/razaumair2203-ux/prose-objective-audit.git ~/.codex/skills/prose-objective-audit
```

If that folder already exists, preserve it and compare versions before replacing it. The skill has no required model API or third-party Python dependencies. Its optional helper requires **Python 3.12 or later**. Reading and rebuilding PDF, Word or LaTeX documents requires the appropriate tools in your environment.

## Use

Invoke `$prose-objective-audit` and give it the reader, document objective, source of record and available evidence. Say whether you want proposals or applied edits. For example:

> Use $prose-objective-audit to audit this report for a technical reader. Check the argument and numerical claims against the supplied tables. Propose exact edits, retain sound wording, and state what you could not verify.

An audit request defaults to proposals. It does not authorize publication or external messages. Independent review is proportionate to the task and applicable project requirements; multiple models are not required for ordinary editing.

Read [SKILL.md](SKILL.md) for the workflow and [the record contract](references/records.md) before using the helper. Run the following from the document's project root, replacing `SKILL_DIR` with this repository's absolute path:

```text
python SKILL_DIR/scripts/audit_guard.py snapshot --root . --files report.md --evidence facts.txt --out WORK/audit/snapshot.json
python SKILL_DIR/scripts/audit_guard.py check --root . --snapshot WORK/audit/snapshot.json --record WORK/audit/review.json
python SKILL_DIR/scripts/audit_guard.py stage --root . --snapshot WORK/audit/snapshot.json --record WORK/audit/review.json --out WORK/audit/staged
```

Write the review record after actually reading the material. Do not auto-fill reader attestations from matching quotes. The helper stages validated edits into a new directory and leaves the original files untouched. For generated documents, authorized changes still need to go through the real editable source, build process and derived-copy checks.

## Tests and limits

```sh
python -B -m unittest discover -s tests -v
```

The tests cover source/evidence binding, exact replacements, overlapping edits, generated inputs, rollback, path checks, supported corrections and context-sensitive token checks. They include sound controls and known limits. See [VALIDATION.md](VALIDATION.md) for the release evidence and its scope.

Paragraph inventories support CR, LF and CRLF, including mixed endings and blank separator lines, without normalizing source bytes or edit offsets. If an older snapshot groups the source differently, regenerate it and genuinely re-attest the new units. The root name `staged_manifest.json` is reserved for staging metadata (case-insensitively); a nested file with that basename remains allowed. See the record contract for compatibility and parser limits.

[Synthetic prose cases](tests/fixtures/prose-review-cases.md) and their [separate author notes](tests/fixtures/prose-review-notes.md) support manual editorial regression checks. Withhold the notes until a reader's report is frozen; alternate evidence-supported wording is acceptable. These are now public maintenance fixtures, not a hidden benchmark. The unit suite does not automatically judge their semantics. [Scope development cases](tests/fixtures/scope-development-cases.md) exercise comparison, fitting and aggregate claims with sound controls. Future independent holdout evaluations need fresh examples, not this answer-bearing corpus.

Token checks read edits in complete document context. They catch a unit-only `ms` → `s` change in `12 ms` and removal of a contraction suffix. Capitalization and apostrophe typography alone do not change strength tokens. Reordered qualifiers still require explicit scope review; an honestly assessed meaning-preserving reorder does not need scientific evidence solely because its token order changed.

These checks remain incomplete heuristics. A false meaning or support assessment can pass. Native rendering, audience comprehension, factual support and scientific validity require real inspection and judgment. No test count or reviewer verdict establishes optimality, editorial superiority, publication readiness or acceptance.

## Revision history

Detailed changes, checks and limits are retained in [VALIDATION.md](VALIDATION.md). Git commits identify the public versions; no new editorial-performance claim is implied by a version update.

| Version | Change and details |
| --- | --- |
| Latest: helper documentation consolidation | Shorter entrypoint; helper commands and detailed limits maintained in the record contract. [Validation](VALIDATION.md#14-november-2026-helper-documentation-consolidation). |
| [0ac3a670](https://github.com/razaumair2203-ux/prose-objective-audit/commit/0ac3a670e5df98deae7edb380a0ce3ffb4ec0d8b) | Compare revised titles, abstract openings and contributions with earlier accepted versions while retaining evidence-based qualifications. [Validation](VALIDATION.md#14-november-2026-accepted-version-comparison). |
| [d7c7408](https://github.com/razaumair2203-ux/prose-objective-audit/commit/d7c7408af381eb101402822436ecf15d3f4af029) | Introduction orientation, conversational provenance and false-alarm safeguards; standalone-summary clarification. [Validation](VALIDATION.md#14-november-2026-targeted-reader-checks). |
| [8f9f794](https://github.com/razaumair2203-ux/prose-objective-audit/commit/8f9f794) | Paragraph inventory across line endings and staging-manifest collision protection. [Validation](VALIDATION.md#8-november-2026-paragraph-inventory-and-staging-reservation). |
| [5001979](https://github.com/razaumair2203-ux/prose-objective-audit/commit/5001979) | Initial public skill with contextual edit safeguards. [Validation](VALIDATION.md#earlier-contextual-token-revision-6-november-2026). |
