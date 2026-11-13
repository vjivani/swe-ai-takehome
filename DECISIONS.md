# Time & Motion Study Analyzer — Decisions

## 1. Goal

Convert the narrative study into validated structured output for:

- discrete activities
- worker classifications
- timing consistency checks
- efficiency flags with evidence and recommendations

The implementation prioritizes traceable outputs over freeform summarization.

## 2. Why this architecture

The source text mixes direct observations, inferred durations, and causal hints. A single-pass extraction was too brittle, so the pipeline uses LangGraph to separate:

- first-pass extraction/analysis
- conditional review routing
- targeted deep review for analyses with inefficiency flags

This keeps the normal path simple while spending extra reasoning only where risk is higher.

## 3. Output model choices

The schema is centered on four domain models:

- `Activity`: atomic observed work unit with timing fields
- `WorkerClassification`: role assignment linked to activity IDs
- `TimingAnalysis`: stated vs calculated duration consistency
- `EfficiencyFlag`: issue type, severity, evidence, likely cause, recommendation

`EvidenceRef` is a shared supporting model for source citations. `AnalysisResult` is the required top-level response envelope, and `DeepReviewPatch` is the smaller response envelope used by the deep-review call. `OutputModel` provides the shared strict configuration (`extra="forbid"`).

The final result contains `activities`, `worker_classifications`, `timing_checks`, `efficiency_flags`, `recommendations`, `validation_notes`, and `deep_review_patches`.

Roles and issue types are plain non-empty strings. The model creates concise labels from the source instead of choosing from a hardcoded taxonomy. It is instructed to reuse the exact label for the same concept within one result so clustering remains stable.

## 4. Current graph shape

Implemented nodes:

1. `read_study`
2. `analyze`
3. conditional route from `analyze`:
   - `deep_review` if any efficiency flags exist
   - `review` if no efficiency flags but timing inconsistencies exist
   - `END` otherwise

Both review paths terminate after one pass.

## 5. Conditional routing strategy

Routing is intentionally asymmetric:

- Any inefficiency flag triggers one deep review of the complete analysis.
- Timing-only issues use a general review path.

This matches the requirement that not every observation needs the same depth while avoiding multiple calls for the same analysis.

## 6. Deep review implementation decision

The deep-review node uses a patch pattern without mutating or merging the original analysis:

- send the source text and complete first-pass analysis
- receive one `DeepReviewPatch` with only changed records
- store the raw patch under `AnalysisResult.deep_review_patches`

Benefits:

- one deep-review call regardless of the number of flags
- preserves the original first-pass analysis for comparison
- keeps the reviewer response available for audit and debugging

## 7. Validation and robustness decisions

- OpenAI structured output uses strict JSON schema.
- Schema is normalized so every object explicitly sets `additionalProperties: false` and required keys are explicit.
- Cross-field validators are tolerant where LLM outputs are noisy:
  - contradictory normalized timing fields are cleared/coerced instead of raising hard errors
  - timing status may be normalized (`consistent`/`inconsistent`/`uncertain`) based on deltas

This avoids workflow crashes while still surfacing uncertainty in structured output.

## 8. Observability decision

Long-running calls previously looked stuck. Progress logging is now built in and enabled by default (`ANALYZER_PROGRESS=1` behavior).

The logs show:

- workflow start/end
- initial analysis pass
- review path selection behavior (via emitted stage logs)
- deep-review flag count and completion

## 9. Trade-offs

- Pros:
  - clearer control flow than monolithic prompting
  - better alignment with conditional-depth requirement
  - raw review output is preserved for auditability
  - resilient validation behavior in production-like noisy outputs

- Cons:
  - the deep-review prompt includes the complete analysis and can be large
  - patch contents require a consumer to compare them with the first-pass result
  - strict schemas increase reliability but add integration complexity

## 10. Future improvements

- add timeout/retry policy with partial-result fallback
- scope review payloads if very large studies make the single deep-review call expensive
- add deterministic pre-checks for common timing arithmetic before LLM review
