---
title: "Curriculum Learning Path"
category: concept
tags: [curriculum, learning-path, prerequisites, progression, synthesis]
source_files: [data/raw/artificial_intelligence.md, data/raw/machine_learning.md, data/raw/deep_learning.md, data/raw/computer_vision.md, data/raw/nlp.md, data/raw/data_science.md, data/raw/python_prerequisites.md, data/raw/statistics_prerequisites.md]
last_updated: 2026-08-30
---

# Curriculum Learning Path

← [Back to Index](../index.md)

> **Concept page** — synthesized from all course and prerequisite source files. Not a raw source itself.

## Full Dependency Graph

```
[No prerequisites]
       │
       ▼
CS101  Python Programming Fundamentals
       │
       ├──────────────────────┐
       ▼                      ▼
STAT201  Statistics    (directly into Data Science)
       │
       ├────────────────┐
       ▼                ▼
AI301  Machine Learning   DS301  Data Science
       │                  (applied/workflow track)
       ▼
AI401  Deep Learning
       │
       ├──────────────────────┐
       ▼                      ▼
AI411  Computer Vision    AI412  NLP
       │                      │
       └──────────┬───────────┘
                  ▼
            Capstone Project
```

*Note: AI201 (Artificial Intelligence Foundations) is a standalone survey course with no formal prerequisites and no dependents — it sits beside, not within, the main progression.*

## The Two Tracks

### Track 1: AI Depth Track
`CS101 → STAT201 → AI301 → AI401 → AI411 / AI412`

The sequential ladder from Python basics to specialized deep learning applications. Each step formally requires the previous one. Students who complete this track are ready for original ML/DL research or engineering roles.

### Track 2: Applied Data Science Track
`CS101 → STAT201 → DS301`

A parallel, shorter track focused on end-to-end data workflows and communication. Draws on ML techniques but at an applied level rather than algorithmic depth. Does not block or require the AI Depth Track.

## Critical Bottleneck Courses

| Course | Why it's a bottleneck |
|--------|----------------------|
| [CS101 Python Fundamentals](../prerequisites/python_programming_fundamentals.md) | Required by STAT201, which is required by AI301 and DS301 — the root of nearly all paths |
| [AI301 Machine Learning](../courses/machine_learning.md) | Gateway to the entire deep learning and specialization layer |
| [AI401 Deep Learning](../courses/deep_learning.md) | Direct prerequisite for both terminal electives (CV and NLP) |

## Key Distinction: AI201 vs. the Main Track

[Artificial Intelligence Foundations](../courses/artificial_intelligence_foundations.md) (AI201) **surveys** ML and DL as subfields of AI. In the actual course sequence, ML and DL are taken **before** the specializations — AI201 does not position itself as a prerequisite to them. Students should take AI201 for breadth, not as a stepping stone.

## Capstone Guidance

Students in the CV track typically apply vision architectures to image datasets. Students in the NLP track often work on text classification, summarization, or transformer-based systems. Both should review [Capstone Project Guidelines](../admin/capstone_project_guidelines.md) by Week 1.
