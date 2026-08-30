# Source Fidelity

## Purpose

Create an auditable chain from every teacher-owned source page to every verbatim sentence used in a generated artifact. Separate extraction from interpretation so the same agent cannot silently rewrite source text and then approve its own rewrite.

## Extraction Modes

Use the least destructive reliable method:

1. `text_layer`: use when the PDF text order is reliable.
2. `ocr`: use for scans or images without a usable text layer.
3. `vision_manual`: use for mixed layouts, diagrams, tables, or OCR failures.
4. `manual_verified`: use after a human has checked the extracted text against the rendered page.

OCR means Optical Character Recognition. Record `ocr_confidence` when the engine provides it, but never use a high score as a substitute for visual review. A low score identifies likely errors; a high score does not prove punctuation, reading order, or region boundaries.

## Extraction Quality

Assign one quality value per source and per difficult page:

- `good`: text order, paragraph breaks, and labels are reliable.
- `mixed`: body text is usable but layout, captions, or exercises require visual checking.
- `poor`: rely on rendered pages plus OCR/vision and mandatory manual verification.
- `blocked`: the source cannot support faithful production.

Use `review_status` on each sentence:

- `verified`: checked against the rendered source page.
- `needs_review`: usable draft extraction but not yet visually confirmed.
- `blocked`: unreadable or conflicting evidence.

## Region Classification

Classify before sentence numbering:

- `article_body`
- `heading`
- `caption`
- `infographic`
- `exercise`
- `reading_skill`
- `critical_thinking`
- `video_script`
- `header_footer`

Only `article_body` sentences participate in full-article verbatim coverage. Never insert `caption`, `heading`, or `header_footer` text into an article paragraph.

## Stable IDs

Use uppercase, zero-padded identifiers:

```text
REF-U03-A-P04-S02
RE1-U07-B-P02-S05
RE1-U07-VIDEO-L03
RE1-U07-A-EX05
```

Keep the ID stable after creation. Correct the text or metadata without renumbering unless the source structure itself was wrong. Record both `printed_page` and `pdf_page` because they often differ.

## Required Ledger Fields

Start from `../assets/templates/source-ledger.template.json`. Record:

- schema version and Unit ID;
- source title, edition, role, provenance, file fingerprint, and extraction quality;
- component type and order;
- paragraph/region ID and source page;
- sentence ID, exact text, extraction method, OCR confidence when applicable, and review status.

Keep raw PDFs, images, audio, and video outside the skill repository.

## Fidelity Manifest

For each generated artifact, create a source-usage manifest from `../assets/templates/source-usage.template.json`.

Use `coverage_policy`:

- `all_article_sentences`: require every verified `article_body` sentence from the named components exactly once and in source order.
- `selected_excerpts`: verify only the cited verbatim excerpts; do not imply full coverage.

Use `mode`:

- `verbatim`: text must match the ledger.
- `adapted`: include `adaptation_note`; never count it as verbatim coverage.
- `reference_only`: cite a source page or exercise without reproducing it.

## Verification

Run:

```bash
python3 scripts/verify_source_fidelity.py \
  --ledger source-ledger.json \
  --usage teacher-guide.source-usage.json \
  --report teacher-guide.source-report.json
```

The script checks:

- unique and known sentence IDs;
- required sentence coverage;
- duplicate and reordered use;
- exact or formatting-only matches;
- modified text;
- likely sentence merges or splits;
- unresolved or blocked source sentences.

Formatting-only normalization covers whitespace and common typographic quote/dash variants. It does not excuse lexical, grammatical, punctuation-content, or sentence-boundary changes.

## Stop Conditions

Stop the dependent artifact when:

- a required page or component is missing;
- edition or Unit identity is uncertain;
- a required sentence remains `needs_review` or `blocked`;
- OCR/vision cannot reliably separate body text from captions or exercises;
- the fidelity report contains an error;
- the artifact claims full coverage but uses adapted text.
