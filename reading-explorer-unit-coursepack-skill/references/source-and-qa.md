# Source Grounding, DOCX QA, and Privacy

## Authority order

When sources disagree, use this order:

1. verified textbook article for reading facts and exact article language;
2. official answer key for its matching official task, checked against the article;
3. article-specific worksheet answer key;
4. teacher-edited material and teacher notes;
5. supplementary or general prompt banks.

Do not use a lower source to overrule the article. Flag a genuine conflict instead of guessing.

## Extraction and verification

- Prefer reliable text layers for extraction.
- Use OCR or visual reading for scans and mixed layouts.
- Render source pages when layout separates article, caption, question, answer, and word bank.
- Visually verify every article sentence used verbatim and every selected source question.
- Separate article body, headings, captions, exercises, answers, and teacher notes.
- Keep a private source inventory with filenames and SHA-256 values.

## Content alignment

Before DOCX production, verify:

- every selected comprehension item has its complete stem, choices, word bank, or response prompt;
- every closed answer is known;
- every open prompt has criteria;
- every find-the-word/phrase answer occurs in the article;
- sentence exercises practise the intended form without changing the article fact;
- Practice Book, Answer Key, and Teaching Outline use the same exercise numbering and final wording;
- classwork/homework routing references real Practice Book exercises;
- homework is prepared by prior classroom work.

## DOCX workflow

Use the installed `documents` skill and its strict render-and-verify process.

Resolve only the relevant curated exemplar for each artifact type through `approved-layout-exemplars.json`. Verify its path and SHA-256, and record the selected exemplar ID in the project brief. Never scan the entire output tree or compare every approved product. Apply the approved profile in `../assets/templates/docx-style-tokens.json` when no selected exemplar is available.

For every final DOCX:

1. run structural and accessibility audits appropriate to the document;
2. verify table width, grid, cell width, margins, and header-row metadata;
3. render every page;
4. inspect every page at full size;
5. confirm no missing CJK glyphs, clipping, overlap, broken tables, unintended blank pages, isolated headings, cramped text, or inadequate answer space;
6. verify the DOCX archive opens cleanly;
7. bind the final review to SHA-256.

## Three-file cross-check

Check at least:

- all Practice Book exercises appear in the key;
- no obsolete answer remains after a student-page edit;
- every lesson reference resolves to the final exercise number;
- the stated reading mode and lesson count are identical in the brief and outline;
- the number of homework exercise groups exceeds the classwork groups when `majority_homework` is selected;
- the writing model meets its own word range and rubric.

## Public repository boundary

The GitHub repository may include only reusable Skill instructions, original scripts, generic templates, synthetic test data, metadata, license, and ignore rules.

Never publish:

- commercial textbook or worksheet files;
- copied article text, questions, answers, images, or transcripts;
- generated classroom DOCX/PDF files;
- source inventories containing extracted commercial content;
- render images or QA caches;
- student data;
- absolute local paths such as `/Users/...`.

The live `approved-layout-exemplars.json` is also private because it points to local generated artifacts. Publish only its generic template.
