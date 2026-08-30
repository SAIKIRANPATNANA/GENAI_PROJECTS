# Wiki Activity Log

Append-only record of ingests, queries, and maintenance passes.
Format: `## [YYYY-MM-DD] <type> | <description>`

Quick grep: `grep "^## \[" log.md | tail -10`

---

## [2026-08-30] ingest | Initial batch — 10 raw source files

**Sources processed:**
- `raw/python_prerequisites.md` → `wiki/prerequisites/python_programming_fundamentals.md`
- `raw/statistics_prerequisites.md` → `wiki/prerequisites/statistics_for_data_driven_fields.md`
- `raw/artificial_intelligence.md` → `wiki/courses/artificial_intelligence_foundations.md`
- `raw/machine_learning.md` → `wiki/courses/machine_learning.md`
- `raw/deep_learning.md` → `wiki/courses/deep_learning.md`
- `raw/data_science.md` → `wiki/courses/data_science.md`
- `raw/computer_vision.md` → `wiki/courses/computer_vision.md`
- `raw/nlp.md` → `wiki/courses/nlp.md`
- `raw/curriculum_rules.md` → `wiki/admin/curriculum_rules.md`
- `raw/project_guidelines.md` → `wiki/admin/capstone_project_guidelines.md`

**Synthesized pages created:**
- `wiki/concepts/curriculum_learning_path.md` — full dependency graph, two curriculum tracks, bottleneck analysis

**Schema created:**
- `AGENTS.md` — governing conventions, directory layout, workflows

**Pages touched:** 11 wiki pages + index.md + log.md + AGENTS.md
