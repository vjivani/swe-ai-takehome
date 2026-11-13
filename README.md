# Take-Home: Time & Motion Study Analyzer

## Overview

Build a LangGraph workflow that analyzes a time and motion study report and produces structured output.

This should take no longer than **1 hour**. Use any AI coding tools available to you (Claude Code, Codex, Copilot, Cursor, etc.). Be prepared to talk through your code in the follow-up interview, and we may ask you to extend the code in a simple way. 

## The Problem

The file `data/time_motion_study.md` contains a narrative time and motion study — observations of workers performing tasks at a manufacturing facility. Your job is to build a pipeline that takes this document and produces structured, validated output.

## Requirements

Your pipeline should extract and structure the following from the study:

**Activities:** Each discrete activity observed (what was done, by whom, where, and for how long).

**Worker Classifications:** Group workers by their observed role (e.g., machine operator, quality inspector, material handler) based on what they were seen doing.

**Timing Analysis:** Normalize all timings into a consistent format. Flag any timings that seem inconsistent with the narrative (e.g., a stated duration that doesn't match a start/end time).

**Efficiency Flags:** Identify potential inefficiencies:
- Wait times or idle periods
- Repeated trips or unnecessary movement
- Bottlenecks where multiple workers are queued
- Any activity that appears duplicated across workers

## What We Expect You to Build

- **Pydantic models** for your output schema — you decide the structure
- **A LangGraph graph** that processes the document through multiple stages
- **Conditional routing** — not every observation needs the same depth of analysis. For example, activities flagged as potentially inefficient could be routed through a deeper analysis node.
- **At least one validation loop** — the pipeline should cross-check its own extractions against the source text and correct or flag inconsistencies
- **A `DECISIONS.md`** explaining your approach: why you structured the models the way you did, why your graph has the shape it does, and any trade-offs you made

## Setup

```bash
# Install dependencies (pip or uv)
pip install .
# or
uv sync

# Run your pipeline
python main.py
```

You'll need an API key for at least one LLM provider (OpenAI or Anthropic). Use whichever you're comfortable with. If cost is a concern, smaller models are fine for this task — we're evaluating your pipeline design, not the model's output quality.

The output should be the structured data your pipeline produces — printed to stdout or written to a file, your choice. We should be able to see the extracted activities, worker classifications, timing analysis, and efficiency flags. Format is up to you (JSON, formatted text, etc.).

## What We're Looking For

This is not about volume of code. We value:
- Clean data modeling (how you structure the output schema)
- Thoughtful graph design (why nodes are split or combined the way they are)
- Validation and self-correction (does the pipeline check its own work?)
- Clear reasoning in DECISIONS.md

## Submission

Clone this repo, complete the work, and push it to a private GitHub repo. Add [INTERVIEWER_GITHUB_USERNAME] as a collaborator so we can review your submission before the follow-up interview. This username will be provided to you separately. 