# QA and Approval

## Production Gates

Use:

`plan -> pilot -> pilot_user_approved -> full -> deliver`

For a new course/level or a material-architecture change, produce at least three representative pilot lessons:

- meaning-first reading;
- sentence-by-sentence language study;
- consolidation, review, output, or media lesson.

Include representative Practice Book pages. Do not enter full production until the user explicitly approves the pilot. Record file paths, ordered artifact roles, SHA-256 values, approval date, approver, and exact approval evidence.

## Specification QA

Run:

```bash
python scripts/validate_coursepack_spec.py coursepack-spec.json
```

Require:

- complete lessons totaling 38–42 minutes;
- an actual lead-in in every lesson;
- teacher moves, ready-to-say language, products, checks, transitions, board plan, homework, and next-lesson check;
- every Practice Book reference resolving to a materialized exercise;
- every closed task having an answer and every open task having criteria;
- homework using taught content for 15–30 minutes;
- oral homework using teacher-verifiable completion;
- no same-surface classwork/homework duplication;
- source and language coverage complete for the declared scope.

## DOCX Content Audit

Run:

```bash
python scripts/audit_coursepack_docx.py --role practice-book --spec coursepack-spec.json Student_Practice_Book.docx
python scripts/audit_coursepack_docx.py --role teacher-guide --spec coursepack-spec.json Teacher_Unit_Guide.docx
```

Resolve every error. Warnings require human review.

## Practice Book Human Review

Check:

- general printed-workbook appearance;
- no teacher/activity/event language;
- no productive/recognition or build metadata;
- exercise action and answer location immediately clear;
- word/blank/option counts explicit and correct;
- active-language staircase visible across the book;
- sentence and grammar practice substantial, not trivial;
- classwork/homework answer routes different;
- response space fits the product;
- answer key complete in Teacher Guide.

## Teacher Guide Human Review

Check every lesson for:

- introduction/lead-in;
- complete 40-minute route;
- actual teacher and student actions;
- ready-to-say English where precision matters;
- material/preparation/display/board requirements;
- checking, anticipated errors, and recovery;
- optional activity with individual evidence when used;
- lesson close;
- Practice Book and homework routing;
- next-lesson check;
- answers and judgment criteria.

Reject a guide that contains only a Unit route, exercise allocation, and answer key.

## Visual QA

Render and inspect every DOCX page at full size. Contact sheets help navigation but do not count as inspection evidence.

Reject:

- unintended blank or near-blank pages;
- missing CJK glyphs or font substitution;
- clipped text, broken tables, overlap, or awkward page breaks;
- cramped student text or tiny answer lines;
- exercise heading separated from its instruction/items;
- response space moved to another page;
- near-empty areas that conceal missing content;
- color-dependent instructions;
- all-capital display labels.

Record separate content, language, sequence, source/copyright, and visual reviews bound to the final SHA-256 values.

## Repository QA

Before GitHub publication, run:

```bash
python scripts/validate_skill_repo.py <repository-root>
```

The repository may contain only the skill, original scripts/references/templates, synthetic samples, metadata, license, and ignore rules. Never publish source books, readings, screenshots, copied exercises, generated classroom DOCX files, teacher/student data, absolute local paths, renders, or QA caches.
