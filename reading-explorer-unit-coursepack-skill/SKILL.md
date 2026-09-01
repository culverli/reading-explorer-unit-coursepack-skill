---
name: reading-explorer-unit-coursepack-skill
description: Build source-grounded, article-level Reading Explorer teaching packs from teacher-owned textbook pages and supplementary exercise materials. Use when Codex needs to create or revise the approved three-piece set—Student Practice Book, Answer Key, and concise Teaching Outline—for Foundations or RE1; when the teacher must first choose intensive or extensive reading, lesson count, and teaching flow; or when selecting textbook comprehension questions, Bloom-style short answers, vocabulary, phrases, grammar cloze, sentence practice, translation, summary, and writing tasks without inventing unsupported source content.
---

# Reading Explorer Article Coursepack

Build a usable three-piece teaching pack from the teacher's own sources. Treat the latest teacher-edited Unit 1A pilot as the layout authority and the two successfully taught lessons as approval of this workflow.

## Default artifact contract

Create these three DOCX files unless the user requests a smaller scope:

1. `Student_Practice_Book.docx`
2. `Practice_Book_Answer_Key.docx`
3. `Teaching_Outline.docx`

Keep the Teaching Outline concise. Do not revive the former full Teacher Unit Guide contract unless the user explicitly asks for one.

## Mandatory intake gate

Do not begin exercise writing from memory or from the Reading Explorer title alone.

When source materials have not been supplied, ask for the recurring package described in [intake-and-reading-modes.md](references/intake-and-reading-modes.md). At minimum, request:

- the textbook article pages or a verified reading body;
- the textbook question/vocabulary pages that may be reused;
- the relevant supplementary pack, workbook, Bloom-question resource, cloze sheet, pre-/post-reading material, or teacher notes;
- the latest teacher-edited sample when its layout should be followed;
- optional audio, video, or transcript when it belongs to the requested scope.

In the same intake, ask these three questions exactly or in equally direct wording:

1. Is this article for **intensive reading（精读）** or **extensive reading（泛读）**?
2. How many lessons are planned, and how many minutes is each lesson?
3. What teaching flow do you already have in mind?

Ask only the smallest additional question needed to resolve a real decision, such as student level, access to the textbook, or classwork/homework balance. If the article itself is missing or unreadable, stop the dependent work. If a supplementary source is unavailable, state the resulting limitation and proceed only after the teacher accepts it.

Record the decisions in `article-project-brief.json`. Initialize a private project with `scripts/init_article_project.py` and validate the brief with `scripts/validate_article_brief.py` before producing final artifacts.

## Workflow

1. **Inspect and fingerprint sources.** Separate the article, textbook multiple-choice questions, vocabulary tasks, Bloom prompts, cloze material, answer pages, and teacher-edited layout sample. Keep commercial files outside the public Skill folder.
2. **Confirm the reading mode.** Read [intake-and-reading-modes.md](references/intake-and-reading-modes.md). Follow the teacher's stated mode instead of assuming every Reading A is deep reading.
3. **Build a source map.** Record which source supports each selected comprehension item and which article sentence supports each authored vocabulary, phrase, grammar, or sentence task.
4. **Select before authoring.** Re-typeset suitable source questions first. Author new exercises mainly for vocabulary, phrases, sentence patterns, translation, summary, and writing when the supplied materials do not already provide enough practice.
5. **Design the Practice Book.** Read [practice-book-standard.md](references/practice-book-standard.md) and [teacher-edited-layout-delta.md](references/teacher-edited-layout-delta.md). Follow the teacher-edited layout hierarchy, typography, spacing, response-space logic, English/Chinese boundary, and green/gold visual system.
6. **Create the Answer Key.** Read [answer-key-standard.md](references/answer-key-standard.md). Give exact closed answers, acceptable open responses, and concise marking criteria.
7. **Create the Teaching Outline.** Read [teaching-outline-standard.md](references/teaching-outline-standard.md). Route a small number of pivotal exercises to class and the majority to homework unless the teacher chooses otherwise.
8. **Generate and verify DOCX.** Use the installed `documents` skill. Apply `assets/templates/docx-style-tokens.json`, render every page, inspect every page at full size, and complete the checks in [source-and-qa.md](references/source-and-qa.md).
9. **Deliver only requested artifacts.** Keep sources, extracted textbook text, working ledgers, renders, and private paths out of GitHub.

## Source-grounded exercise policy

- Use textbook multiple-choice questions for quick comprehension when suitable.
- Use supplied Bloom prompts for short answers, deeper comprehension, and critical thinking; adapt wording to the learner level without changing the supported idea.
- Build find-the-word and find-the-phrase tasks from meanings that actually resolve to the article.
- Move vocabulary beyond isolated words into complete sentence contexts.
- Select high-value article sentence frames and practise them through correction, combination, transformation, guided sentence writing, or Chinese-to-English translation.
- Use supplied cloze, pre-/post-reading, and worksheet content selectively. Do not include every available task merely because it exists.
- Prefer assembling strong source questions over manufacturing new comprehension questions. Every new comprehension item must be answerable from the verified article.
- Give every closed task an answer and every open task judgment criteria.

## Intensive and extensive reading

For **intensive reading**, normally move from quick comprehension to Bloom-style short answers, vocabulary and phrases, high-value sentence work, text rebuilding/summary, and a short final output. Allocate more rereading and language practice.

For **extensive reading**, a short grammar cloze before revealing the article is valid when it activates familiar grammar and creates curiosity. Keep it brief, use a selected excerpt or concise source-grounded version, then reveal the article for timed reading, gist/detail checking, and only selective language follow-up. Do not let the cloze consume the reading lesson or introduce untaught grammar. Read the full guardrails in [intake-and-reading-modes.md](references/intake-and-reading-modes.md).

## Student/teacher boundary

Keep only learner actions, exercise content, examples, word banks, and response spaces in the Practice Book. Keep lesson timing, classwork/homework assignment, checking moves, board plan, answer logic, and teacher rationale in the Teaching Outline or Answer Key.

Use concrete learner-facing directions. Raise the thinking demand through the text and required response, not through abstract teaching terminology.

## Stop conditions

Stop the dependent artifact when:

- the article, edition, or requested reading is uncertain;
- the source pages have not been visually verified;
- the teacher has not answered reading mode, lesson count/duration, or intended flow;
- a comprehension item is unsupported by the article;
- a vocabulary or phrase-search answer does not occur in the article;
- homework introduces language or task types not prepared in class;
- a closed task lacks an answer or an open task lacks criteria;
- the three artifacts disagree on exercise number, wording, lesson route, or marking;
- any DOCX page has clipping, missing glyphs, broken tables, awkward page breaks, cramped text, or inadequate response space;
- a public repository contains commercial material, generated classroom documents, private paths, or source-derived text.
