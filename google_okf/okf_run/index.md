---
okf_version: "0.2"
---

# AI/Cybersecurity Learning Knowledge Bundle

An OKF v0.2 bundle capturing the academic curriculum for the AI/Cybersecurity program. All concepts are derived from raw source documents in `data/raw/` and are maintained as interlinked, agent-readable markdown files.

# Directories

* [courses/](courses/) — Academic course concepts organized by prerequisite tier
* [policies/](policies/) — Administrative policy documents

# Quick Reference: Prerequisite Graph

```
CS101 (Python)
  └─► STAT201 (Statistics)
        └─► AI301 (Machine Learning)  ─► DS301 (Data Science)
               └─► AI401 (Deep Learning)
                     ├─► AI411 (Computer Vision)
                     └─► AI412 (NLP)

AI201 (AI Foundations)  — standalone survey, no prerequisites
```

# Concepts by Type

## Course

* [Python Programming Fundamentals](courses/python_prerequisites.md) — CS101
* [Artificial Intelligence Foundations](courses/artificial_intelligence.md) — AI201
* [Statistics for Data-Driven Fields](courses/statistics_prerequisites.md) — STAT201
* [Machine Learning](courses/machine_learning.md) — AI301
* [Data Science](courses/data_science.md) — DS301
* [Deep Learning](courses/deep_learning.md) — AI401
* [Computer Vision](courses/computer_vision.md) — AI411
* [Natural Language Processing](courses/nlp.md) — AI412

## Policy

* [Curriculum Examination and Grading Rules](policies/curriculum_rules.md)
* [Capstone Project Guidelines](policies/project_guidelines.md)
