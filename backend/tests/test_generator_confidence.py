from app.rag.generator import calculate_confidence


def test_no_chunks_is_low_confidence():
    assert calculate_confidence([]) == "low"


def test_confidence_uses_best_score_not_the_first_chunk():
    assert calculate_confidence([{"score": 0.80}, {"score": 0.30}]) == "high"


def test_high_confidence_boundary():
    assert calculate_confidence([{"score": 0.45}]) == "high"
    assert calculate_confidence([{"score": 0.46}]) == "medium"


def test_medium_confidence_boundary():
    assert calculate_confidence([{"score": 0.70}]) == "medium"
    assert calculate_confidence([{"score": 0.71}]) == "low"


def test_all_weak_chunks_stay_low():
    assert calculate_confidence([{"score": 0.90}, {"score": 0.85}]) == "low"
