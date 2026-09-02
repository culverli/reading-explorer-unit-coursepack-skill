# Curated Layout Exemplar Selection

## Purpose

Use a small, teacher-approved set of representative artifacts to guide formatting. This is not an archive or a complete register of everything the Skill has produced.

The live workspace index is `approved-layout-exemplars.json`. It belongs at the workspace root, alongside the private source and output roots, rather than inside each article folder. Treat its recorded artifact paths as relative to the workspace root. The public Skill contains only `assets/templates/approved-layout-exemplars.template.json`.

## Selection rule

For each requested artifact type:

1. Read the index, not the entire output directory.
2. Select the highest-priority compatible exemplar.
3. Open one exemplar by default.
4. Open a second exemplar only when it is explicitly tagged for the requested level, reading mode, or substantially different task architecture.
5. Never open more than two exemplars for one artifact type.

When producing the default three-piece set, it is valid to select one Practice Book, one Answer Key, and one Teaching Outline exemplar. Do not treat twenty approved coursepacks as twenty required references.

## Compatibility and precedence

Use this precedence:

1. teacher-selected exemplar for the current request;
2. primary exemplar matching artifact type and level;
3. primary exemplar matching artifact type;
4. portable standards and DOCX style tokens in this Skill.

Do not add a newly approved product automatically. Add it only when the teacher identifies it as a replacement exemplar or it captures a genuinely new reusable layout pattern. Deprecate superseded entries instead of deleting historical paths when the history remains useful.

## Path and integrity checks

- Resolve relative paths from the directory containing the index.
- Reject a missing path, wrong artifact type, or SHA-256 mismatch.
- Do not fall back to searching every output folder.
- If an indexed exemplar is unavailable, use the portable standard and note that visual comparison was unavailable.
- Keep generated artifacts and the live index out of the public repository.

Validate a live index and its targets before production:

`python scripts/validate_layout_exemplars.py /path/to/approved-layout-exemplars.json --check-files`
