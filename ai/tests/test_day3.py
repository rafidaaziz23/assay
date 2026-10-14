"""Day 3 units: calibration labels and the appeal handler (offline shapes)."""
import ai


def test_calibration_boundaries():
    assert ai.calibration_label(86, 70)["label"] == "overconfident"      # gap +16
    assert ai.calibration_label(85, 70)["label"] == "well_calibrated"    # gap +15
    assert ai.calibration_label(54, 70)["label"] == "underconfident"     # gap -16
    assert ai.calibration_label(55, 70)["label"] == "well_calibrated"    # gap -15
    assert ai.calibration_label(70, 70)["label"] == "well_calibrated"


def test_calibration_gap_value():
    out = ai.calibration_label(90, 75)
    assert out["calibration_gap"] == 15
    assert out["label"] == "well_calibrated"


def test_appeal_shape():
    out = ai.appeal("ch_01", "The honeypot penalty was unfair.")
    assert out["appeal_id"].startswith("apl_")
    assert out["chapter_id"] == "ch_01"
    assert out["status"] == "under_review"
    assert out["reviewer"] == "verifier_model"
    assert out["possible_outcome"] == ["upheld", "score_revised", "re_interview"]
