---
name: reading-explorer-unit-coursepack-skill
description: Build source-grounded Reading Explorer coursepacks for Grade 6 from teacher-owned books, readings, exercises, images, audio, video, and transcripts. Use when creating or revising a complete lesson-by-lesson Teacher Guide and a merged printable Practice Book for Reading Explorer Foundations or RE1; when planning Deep Reading A, Transfer Reading B, video/listening, vocabulary, chunks, grammar, retelling, homework, games, and review; or when validating source fidelity, exercise clarity, lesson completeness, DOCX layout, pilot approval, and GitHub-safe packaging.
---

# Reading Explorer Unit Coursepack

Build a teachable Reading Explorer Unit, not a textbook summary and not a set of attractive generic worksheets. Preserve source truth, teach language explicitly, and make every printed exercise immediately completable.

## Approved Artifact Contract

Produce two student/teacher artifacts by default:

1. `Teacher_Unit_Guide.docx` — a complete lesson-by-lesson 40-minute teaching guide.
2. `Student_Practice_Book.docx` — one general-purpose printed exercise book used for both classwork and homework.

Do not create a separate Homework Booklet, Classroom Display PPT, or fixed Activity Kit unless the user explicitly requests one. Route classwork and homework by Practice Book exercise number inside the Teacher Guide. Keep optional cards or jigsaw sheets in a Teacher Guide appendix only when the activity genuinely requires them.

The approved Practice Book authority is the teacher-reviewed five-page Unit 1A sample described in [approved-practice-book-standard.md](references/approved-practice-book-standard.md). Preserve its functional hierarchy, density, task grammar, and student/teacher boundary without copying its source-derived content into this repository.

## Required Workflow

1. **Inspect the request and sources.** Record learner profile, Reading Explorer level/edition, Unit, lesson duration, source pages, available media, printing constraints, and whether students own the book. Mark unknown decisions `needs_review`.
2. **Create the private project.** Run `scripts/init_coursepack_project.py <project-dir>`. Keep teacher-owned sources and generated classroom artifacts outside this public skill folder.
3. **Build source truth.** Read [source-fidelity.md](references/source-fidelity.md). Separate article body, headings, captions, exercises, Reading Skill, infographics, and media scripts. Verify source sentences against rendered pages before close study.
4. **Design the Unit path.** Read [instructional-system.md](references/instructional-system.md) and [learner-and-difficulty.md](references/learner-and-difficulty.md). Plan Reading A as Deep Reading, Reading B as Transfer Reading, then video/listening, integrated output, retrieval, feedback, and homework.
5. **Map language coverage.** For every Reading A sentence, record meaning, first-encounter vocabulary, English definitions, chunks/collocations, useful grammar/pattern, Practice Book evidence, later retrieval, and teacher notes. Simple sentences may take little time; none may silently disappear from the teacher ledger.
6. **Materialize every lesson.** Read [teacher-guide-standard.md](references/teacher-guide-standard.md). Each lesson must include its introduction/lead-in, purpose, materials, preparation, timed stages, teacher moves, ready-to-say English, student product, checks, transitions, board plan, optional interaction, lesson close, homework, and next-lesson check.
7. **Materialize the Practice Book.** Read [practice-book-standard.md](references/practice-book-standard.md). Write stable exercises for a general learner audience. Keep classroom organization, team scoring, teacher checks, and assignment decisions out of student pages.
8. **Validate before DOCX production.** Run `scripts/validate_coursepack_spec.py <coursepack-spec.json>`. Fix every error. A planning outline or exercise list is not a finished specification.
9. **Produce a pilot.** Generate representative meaning-first, close-study, and consolidation/review lessons plus representative Practice Book pages. Do not generate the complete Unit until the teacher explicitly approves the pilot. Bind approval to SHA-256 in `pilot-approval.json`.
10. **Generate the two DOCX files.** Use the installed `documents` skill. Reuse the page tokens and component patterns in `assets/templates/docx-style-tokens.json` and `scripts/build_synthetic_reference.py`; do not reuse the synthetic wording as course content.
11. **Audit and render.** Run `scripts/audit_coursepack_docx.py` on both DOCX files, render every page, and inspect every page at full size. Read [qa-and-approval.md](references/qa-and-approval.md).
12. **Deliver cleanly.** Return only requested final artifacts. Keep commercial pages, source ledgers containing textbook text, extraction caches, renders, and QA scratch files out of GitHub.

## Instructional Non-Negotiables

- Treat context as the vehicle for language learning, not as a substitute for it.
- Keep Reading A meaning-first for at least two lessons before systematic sentence-by-sentence language study.
- Teach active vocabulary at first encounter with an age-appropriate English definition, source context, useful chunk/collocation, controlled accuracy work, and new-context use.
- Put meaningful input before open output and comprehension before explanation-heavy language work.
- Move from quick recognition to precision/repair, guided use, independent new-context use, and delayed retrieval.
- Make homework 15–30 minutes, based only on taught content, and different from the same-day classwork surface task and answer route.
- State a teacher-verifiable route for oral homework; peer rehearsal alone is not completion evidence.
- Give speaking quiet preparation and rehearsal before public checking.
- Require individual evidence inside pair, team, competition, or jigsaw work.
- Use games selectively. Require a language purpose plus at least two of: right/wrong judgment, scoring, evidence, construction/repair, strategy, time pressure, or competition.

## Student/Teacher Boundary

Keep these only in the Teacher Guide or internal specification:

- productive/recognition tiers and language-selection rationale;
- complete sentence analysis and completed notes;
- lesson aims, timing, grouping, teacher questions, transitions, scores, random checks, and next-lesson use;
- source IDs, checkpoints, build stages, pilot metadata, and answer keys.

Keep these in the Practice Book:

- reading-body image only when the private project has permission to reproduce it;
- concise exercise headings and direct instructions;
- English-definition vocabulary work, chunks, forms, sentence/grammar practice, text building, evidence, retelling, review, and transfer;
- examples/support only when needed to complete the task;
- response space shaped to the requested product.

## Reference Routing

- Read [approved-practice-book-standard.md](references/approved-practice-book-standard.md) before any Practice Book design or review.
- Read [teacher-guide-standard.md](references/teacher-guide-standard.md) before any Teacher Guide design or review.
- Read [practice-book-standard.md](references/practice-book-standard.md) before writing student exercises.
- Read [instructional-system.md](references/instructional-system.md) before allocating lessons, language work, homework, or output.
- Read [source-fidelity.md](references/source-fidelity.md) for extraction, sentence IDs, and verbatim verification.
- Read [learner-and-difficulty.md](references/learner-and-difficulty.md) before calibrating support and challenge.
- Read [grammar-progression.md](references/grammar-progression.md) before selecting grammar or sentence targets.
- Read [activity-design.md](references/activity-design.md) before creating a game, competition, jigsaw, movement, pair, or group task.
- Read [qa-and-approval.md](references/qa-and-approval.md) before pilot approval, full production, or delivery.
- Read [provenance.md](references/provenance.md) before GitHub publication or redistribution.

## Stop Conditions

Stop the dependent artifact when:

- the edition, page, reading body, or media source is uncertain;
- source extraction has not been visually verified;
- a lesson is only a route table or answer key rather than a complete teachable design;
- a Practice Book exercise depends on missing textbook questions, missing screen content, or an unstated teacher explanation;
- new vocabulary/grammar appears first in homework;
- a student exercise exposes teacher/design metalanguage or has no clear action/answer location;
- the Practice Book repeats classwork as homework with only cosmetic changes;
- a closed task lacks an answer, or an open task lacks judgment criteria;
- the representative pilot has not been explicitly approved;
- any DOCX page has clipping, missing glyphs, unintended blanks, cramped text, broken tables, or missing response space;
- a public repository contains commercial, teacher-owned, source-derived, or private-path material.
