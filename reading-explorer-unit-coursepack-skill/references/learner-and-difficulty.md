# Learner Calibration and Text Difficulty

## Three Independent Axes

Make every calibration decision from three separate inputs:

1. `book_level`: the language baseline of Foundations or RE1.
2. `cohort_profile`: Grade 6 age, proficiency range, class size, strengths, needs, and classroom constraints.
3. `article_difficulty`: the lexical, syntactic, discourse, knowledge, and task demands of the actual Reading A/B text.

Do not convert a Reading Explorer level into a school grade. Two Grade 6 cohorts may use Foundations and RE1 while sharing the same cognitive maturity.

## Age-Respectful Accessibility

For both Foundations and RE1:

- use topics, examples, humor, visuals, competition, and choices suitable for 11–12-year-olds;
- simplify sentence structure, directions, or support rather than making content infantile;
- avoid babyish examples such as isolated `dog / cake / big` unless the source requires them;
- prefer school life, friendship, sport, nature, technology, culture, exploration, and real-world problems;
- keep public performance supported by quiet preparation and pair rehearsal.

## Foundations Calibration

Use more access support:

- shorter directions and one action per numbered item;
- visible examples, word banks, chunks, diagrams, and rehearsal notes;
- explicit sentence-component labels;
- controlled practice before guided production;
- reduced lexical load while maintaining Grade 6 cognitive interest.

Do not assume that Foundations learners need low-level thinking. They may infer, compare, justify, create, and evaluate when the language support is sufficient.

## RE1 Calibration

Use less support and deeper language analysis:

- longer evidence-based responses;
- reduced word-bank dependence;
- more clause identification and sentence combination;
- stronger guided-to-independent vocabulary and grammar use;
- more cross-text comparison, inference, evaluation, and transfer.

## Actual Difficulty Profile

Run `scripts/analyze_text_difficulty.py` on the verified source ledger. Treat its output as descriptive evidence, not an automatic placement decision.

Record for Reading A and Reading B separately:

- sentence and word counts;
- mean, median, maximum, and upper-quartile sentence length;
- number and percentage of sentences above 15 and 20 words;
- unique-word count and type-token ratio, interpreted cautiously for short texts;
- long-word ratio;
- clause-marker density and likely multi-clause sentences;
- the most demanding sentences and why they were flagged;
- optional cohort-lexicon coverage when a teacher-provided known-word list exists;
- discourse pattern, background-knowledge load, visual load, and task demand added by human review.

Never label a text `easy` or `hard` from sentence length alone. Use the profile to decide:

- estimated module range;
- amount and type of vocabulary support;
- sentence-analysis targets;
- number of rereads/listens;
- retelling scaffold level;
- Core versus Plus differentiation.

## Differentiation

Keep one central objective while changing access or depth:

- access: word bank, chunking, model, sentence frame, visual support, extra processing time, partner rehearsal;
- extension: justification, synthesis, audience change, reduced scaffolding, additional evidence, comparison.

Do not respond to proficiency differences merely by giving weaker learners fewer questions and stronger learners more questions.
