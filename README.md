# Reading Explorer Article Coursepack Skill

A reusable Codex Skill for turning teacher-owned Reading Explorer textbook pages and supplementary exercise materials into an article-level teaching pack.

The current default output contract is the classroom-tested three-piece set:

1. `Student_Practice_Book.docx`
2. `Practice_Book_Answer_Key.docx`
3. `Teaching_Outline.docx`

Before production, the Skill asks for the source package and confirms whether the article is intensive or extensive reading, the planned lesson count/duration, and the teacher's intended flow. It then selects suitable source questions, adds article-grounded vocabulary/phrase/sentence practice, routes a small amount of work to class and the majority to homework, and verifies all three DOCX files.

The recurring source intake is organized into nine slots: textbook, worksheet and answers, Bloom prompts, vocabulary materials, pre/post reading, grammar cloze, official extras, teacher notes, and the latest teacher-edited layout authority. The intake is structured; lesson design stays flexible.

The portable Practice Book standard records the teacher's edits to the classroom-tested Unit 1A pilot: 11 pt student text, task-sensitive 1.5/2.0 line spacing, English-only interface language, Chinese retained as translation input, cleaner answer spaces, and the approved green/gold workbook hierarchy.

## Install

Copy or symlink [`reading-explorer-unit-coursepack-skill`](reading-explorer-unit-coursepack-skill) into the Codex skills directory, or clone this repository on another computer and install that folder as a personal Skill.

## Public/private boundary

This repository contains only reusable instructions, validators, templates, and synthetic test data. Commercial textbook pages, supplementary packs, generated classroom DOCX files, extracted article text, renders, and private local paths are intentionally excluded.
