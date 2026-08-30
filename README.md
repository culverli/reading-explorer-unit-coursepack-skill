# Reading Explorer Unit Coursepack Skill

A reusable Codex Skill for building source-grounded Grade 6 Reading Explorer coursepacks from teacher-owned materials.

The default output contract is:

1. a complete lesson-by-lesson `Teacher_Unit_Guide.docx`;
2. one printable `Student_Practice_Book.docx` used for both classwork and homework.

The Skill preserves the approved Practice Book hierarchy and exercise quality while requiring every Teacher Guide lesson to include a real lead-in, a complete 40-minute route, teacher moves, ready-to-say English, checks, transitions, board/display directions, homework, next-lesson use, and answers.

## Install

Copy or symlink [`reading-explorer-unit-coursepack-skill`](reading-explorer-unit-coursepack-skill) into your Codex skills directory, then invoke `$reading-explorer-unit-coursepack-skill` with the teacher-owned source package and learner constraints.

## Validation

The repository includes validators for:

- the two-artifact coursepack specification;
- sentence-level source fidelity;
- Practice Book and Teacher Guide DOCX structure;
- the public repository boundary.

It also includes a fully original synthetic specification and DOCX builder for forward testing. Commercial books, copied readings, generated classroom documents, private paths, and QA renders are intentionally excluded.
