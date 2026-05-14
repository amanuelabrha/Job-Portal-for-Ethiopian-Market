"""TF-IDF + cosine similarity for job–candidate matching.

Scaled to 10k+ documents: fit vectorizer on corpus in batches; cache job vectors in Redis.
This module exposes stateless helpers used by the API layer.
"""
from __future__ import annotations

import hashlib
import re
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_WORD = re.compile(r"[A-Za-zአ-ፚ0-9+#./]{2,}", re.UNICODE)


def tokenize_loose(text: str) -> str:
    """Keep Amharic letters (Unicode block) and Latin tokens for mixed ET CVs."""
    return " ".join(_WORD.findall(text or ""))


def build_job_text(title: str, desc: str, requirements: str) -> str:
    return tokenize_loose(f"{title}\n{desc}\n{requirements}")


def build_candidate_text(profile_blob: str, resume_text: str, skills: Iterable[str]) -> str:
    skills_s = " ".join(skills)
    return tokenize_loose(f"{profile_blob}\n{resume_text}\n{skills_s}")


def compute_match_score(job_text: str, candidate_text: str) -> float:
    if not job_text.strip() or not candidate_text.strip():
        return 0.0
    vec = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=1)
    try:
        m = vec.fit_transform([job_text, candidate_text])
        sim = cosine_similarity(m[0:1], m[1:2])[0, 0]
        return float(max(0.0, min(1.0, sim)))
    except ValueError:
        return 0.0


def batch_scores(job_text: str, candidates: list[str]) -> np.ndarray:
    """Vectorize once per job for many candidates — O(n) transform per candidate set."""
    if not candidates:
        return np.array([])
    corpus = [job_text] + candidates
    vec = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), min_df=1)
    mat = vec.fit_transform(corpus)
    sims = cosine_similarity(mat[0:1], mat[1:]).flatten()
    return np.clip(sims, 0.0, 1.0)


def job_cache_key(job_id: int, job_text: str) -> str:
    h = hashlib.sha256(job_text.encode("utf-8", errors="ignore")).hexdigest()[:16]
    return f"jobvec:{job_id}:{h}"
