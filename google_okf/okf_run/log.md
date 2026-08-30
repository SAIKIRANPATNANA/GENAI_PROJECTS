# Directory Update Log

## 2026-08-30

* **Initialization**: Created OKF v0.2 bundle structure from 10 raw source documents in `data/raw/`.
* **Creation**: Established `courses/` directory with 8 `Course` concept documents:
  - `python_prerequisites.md` (CS101)
  - `statistics_prerequisites.md` (STAT201)
  - `artificial_intelligence.md` (AI201)
  - `machine_learning.md` (AI301)
  - `data_science.md` (DS301)
  - `deep_learning.md` (AI401)
  - `computer_vision.md` (AI411)
  - `nlp.md` (AI412)
* **Creation**: Established `policies/` directory with 2 `Policy` concept documents:
  - `curriculum_rules.md`
  - `project_guidelines.md`
* **Creation**: Added `courses/index.md` with tier-based grouping and `policies/index.md`.
* **Creation**: Added root `index.md` (OKF v0.2) with prerequisite graph and full concept listing.
* **Creation**: Added root `log.md` (this file).
* **Source mapping**: Every concept traces back to its originating raw file via the `sources` frontmatter field.
* **Cross-linking**: All prerequisite and "Leads To" relationships expressed as markdown links between concept files.
