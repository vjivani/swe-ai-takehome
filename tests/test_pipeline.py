from pathlib import Path

import analyzer


def test_analyze_study_uses_review_for_flagged_output(monkeypatch):
    study_path = Path(__file__).resolve().parents[1] / "data" / "time_motion_study.md"
    calls = []
    deep_calls = []
    first_pass = {
        "activities": [
            {
                "activity_id": "ACT_001",
                "day_index": 1,
                "worker": "Maria Chen",
                "role": "soldering_specialist",
                "task": "Soldered PCBs",
                "location": "Station 1",
                "start_raw": "7:06 AM",
                "end_raw": "7:52 AM",
                "start_minute_of_shift": 6,
                "end_minute_of_shift": 52,
                "duration_minutes": 46,
                "evidence": [{"quote": "Maria works through a batch of 24 PCBs.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "source_section": "Morning — Assembly Line Alpha",
                "confidence": 0.9,
            }
        ],
        "worker_classifications": [
            {
                "worker": "Maria Chen",
                "role": "soldering_specialist",
                "station": "Station 1",
                "activity_ids": ["ACT_001"],
                "evidence": [{"quote": "Maria works through a batch of 24 PCBs.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "confidence": 0.9,
            }
        ],
        "timing_checks": [
            {
                "timing_check_id": "TC_001",
                "activity_ids": ["ACT_001"],
                "worker": "Maria Chen",
                "task": "Soldered PCBs",
                "status": "inconsistent",
                "stated_duration_minutes": 44,
                "calculated_duration_minutes": 46,
                "details": "Timing needs review.",
                "evidence": [{"quote": "7:06 AM - 7:52 AM.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
            }
        ],
        "efficiency_flags": [
            {
                "flag_id": "EF_001",
                "issue_type": "upstream_material_wait",
                "severity": "medium",
                "description": "Upstream wait.",
                "workers": ["David Park"],
                "activity_ids": ["ACT_001"],
                "time_window_raw": "7:15 AM - 7:53 AM",
                "evidence": [{"quote": "David waits for the first batch.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "likely_cause": "Station 2 depended on Station 1 completion",
                "recommendation": "Pre-stage work or rebalance handoff timing.",
            }
        ],
        "recommendations": [],
        "validation_notes": [],
    }
    reviewed = {**first_pass, "validation_notes": ["Confirmed cited timing discrepancy against the source."]}

    def fake_generate_analysis(source_text, review_of=None):
        calls.append((source_text, review_of))
        response = first_pass if review_of is None else reviewed
        return analyzer.AnalysisResult.model_validate(response)

    def fake_generate_deep_review(source_text, review_of):
        _ = source_text
        deep_calls.append(review_of)
        return analyzer.DeepReviewPatch.model_validate(
            {
                "activities": [],
                "worker_classifications": [],
                "timing_checks": [],
                "efficiency_flags": [reviewed["efficiency_flags"][0]],
                "recommendations": [],
                "validation_notes": reviewed["validation_notes"],
            }
        )

    monkeypatch.setattr(analyzer, "_generate_analysis", fake_generate_analysis)
    monkeypatch.setattr(analyzer, "_generate_deep_review", fake_generate_deep_review)
    result = analyzer.analyze_study(study_path)

    assert len(result["activities"]) > 0
    assert len(result["worker_classifications"]) > 0
    assert len(result["efficiency_flags"]) > 0
    assert result["validation_notes"] == first_pass["validation_notes"]
    assert len(calls) == 1
    assert calls[0][1] is None
    assert "Riverside Manufacturing" in calls[0][0]
    assert len(deep_calls) == 1
    assert len(result["deep_review_patches"]) == 1
    assert result["deep_review_patches"][0]["efficiency_flags"][0]["flag_id"] == "EF_001"
    assert result["deep_review_patches"][0]["validation_notes"] == reviewed["validation_notes"]


def test_deep_review_preserves_raw_patch_without_merging(monkeypatch):
    study_path = Path(__file__).resolve().parents[1] / "data" / "time_motion_study.md"
    deep_calls = []

    first_pass = {
        "activities": [
            {
                "activity_id": "ACT_001",
                "day_index": 1,
                "worker": "Maria Chen",
                "role": "soldering_specialist",
                "task": "Soldered PCBs",
                "location": "Station 1",
                "start_raw": "7:06 AM",
                "end_raw": "7:52 AM",
                "start_minute_of_shift": 6,
                "end_minute_of_shift": 52,
                "duration_minutes": 46,
                "evidence": [{"quote": "Maria works through a batch of 24 PCBs.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "source_section": "Morning — Assembly Line Alpha",
                "confidence": 0.9,
            }
        ],
        "worker_classifications": [
            {
                "worker": "Maria Chen",
                "role": "soldering_specialist",
                "station": "Station 1",
                "activity_ids": ["ACT_001"],
                "evidence": [{"quote": "Maria works through a batch of 24 PCBs.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "confidence": 0.9,
            }
        ],
        "timing_checks": [
            {
                "timing_check_id": "TC_001",
                "activity_ids": ["ACT_001"],
                "worker": "Maria Chen",
                "task": "Soldered PCBs",
                "status": "consistent",
                "stated_duration_minutes": 46,
                "calculated_duration_minutes": 46,
                "details": "Timing is consistent.",
                "evidence": [{"quote": "7:06 AM - 7:52 AM.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
            }
        ],
        "efficiency_flags": [
            {
                "flag_id": "EF_001",
                "issue_type": "upstream_material_wait",
                "severity": "medium",
                "description": "Upstream wait.",
                "workers": ["David Park"],
                "activity_ids": ["ACT_001"],
                "time_window_raw": "7:15 AM - 7:53 AM",
                "evidence": [{"quote": "David waits for the first batch.", "section": "Morning — Assembly Line Alpha", "day_index": 1}],
                "likely_cause": "Station 2 depended on Station 1 completion",
                "recommendation": "Pre-stage work or rebalance handoff timing.",
            },
            {
                "flag_id": "EF_002",
                "issue_type": "misplaced_component_retrieval",
                "severity": "low",
                "description": "Repeated part retrieval.",
                "workers": ["Leo Tran"],
                "activity_ids": ["ACT_001"],
                "time_window_raw": "8:10 AM - 8:22 AM",
                "evidence": [{"quote": "Leo made two extra trips for parts.", "section": "Materials Handling", "day_index": 1}],
                "likely_cause": "Poor kitting",
                "recommendation": "Prepare complete kits before shift start.",
            },
        ],
        "recommendations": [],
        "validation_notes": [],
    }

    def fake_generate_analysis(source_text, review_of=None):
        _ = source_text
        _ = review_of
        return analyzer.AnalysisResult.model_validate(first_pass)

    def fake_generate_deep_review(source_text, review_of):
        _ = source_text
        deep_calls.append(review_of)
        return analyzer.DeepReviewPatch.model_validate(
            {
                "activities": [],
                "worker_classifications": [],
                "timing_checks": [],
                "efficiency_flags": first_pass["efficiency_flags"],
                "recommendations": [],
                "validation_notes": ["All efficiency flags reviewed."],
            }
        )

    monkeypatch.setattr(analyzer, "_generate_analysis", fake_generate_analysis)
    monkeypatch.setattr(analyzer, "_generate_deep_review", fake_generate_deep_review)

    result = analyzer.analyze_study(study_path)

    assert len(result["efficiency_flags"]) == 2
    assert len(result["deep_review_patches"]) == 1
    assert len(result["deep_review_patches"][0]["efficiency_flags"]) == 2
    assert len(deep_calls) == 1
    assert len(deep_calls[0]["efficiency_flags"]) == 2
