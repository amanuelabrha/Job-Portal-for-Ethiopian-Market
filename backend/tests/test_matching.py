from app.services.matching import batch_scores, build_job_text, compute_match_score


def test_compute_match_score_basic():
    job = build_job_text("Python Developer", "We need django rest", "python sql")
    cand = build_candidate_text("Backend engineer", "python django postgres", ["python", "sql"])
    s = compute_match_score(job, cand)
    assert 0.0 <= s <= 1.0
    assert s > 0.1


def test_batch_scores_ordering():
    job = build_job_text("Nurse", "ICU experience", "amharic english")
    cands = [
        build_candidate_text("nurse icu", "english amharic", ["nursing"]),
        build_candidate_text("cashier", "retail", ["excel"]),
    ]
    scores = batch_scores(job, cands)
    assert scores[0] >= scores[1]

