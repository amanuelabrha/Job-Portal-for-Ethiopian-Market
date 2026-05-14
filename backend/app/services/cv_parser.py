"""CV text extraction and lightweight NLP structuring.

Ethiopian market: many CVs mix English/Amharic; we keep UTF-8 end-to-end.
Optional spaCy improves entity-like chunks when CV_PARSER_MODE=spacy.
"""
from __future__ import annotations

import re
from typing import Any

from app.config import get_settings


def extract_pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    from io import BytesIO

    reader = PdfReader(BytesIO(data))
    parts: list[str] = []
    for page in reader.pages:
        t = page.extract_text() or ""
        parts.append(t)
    return "\n".join(parts).strip()


def extract_docx_text(data: bytes) -> str:
    from io import BytesIO
    from docx import Document

    doc = Document(BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text).strip()


def _heuristic_skills(text: str) -> list[str]:
    common = [
        "python",
        "javascript",
        "typescript",
        "react",
        "next.js",
        "node",
        "fastapi",
        "django",
        "sql",
        "postgresql",
        "aws",
        "docker",
        "kubernetes",
        "excel",
        "sales",
        "marketing",
        "amharic",
        "english",
        "customer service",
        "accounting",
        "finance",
        "civil engineering",
        "nursing",
        "teaching",
    ]
    low = text.lower()
    found = [s for s in common if s in low]
    # also pick Title Case tokens that look like skills (short lines)
    for line in text.splitlines():
        line = line.strip()
        if 2 <= len(line) <= 40 and line[0].isupper() and "@" not in line:
            if line.lower() not in [x.lower() for x in found]:
                if re.match(r"^[A-Za-z][A-Za-z0-9+.#/\-\s]{1,38}$", line):
                    found.append(line)
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for s in found:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out[:40]


def _heuristic_experience(text: str) -> list[dict[str, Any]]:
    """Very simple section split — real deployments should use Affinda/pyresparser."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    blocks: list[dict[str, Any]] = []
    current: list[str] = []
    for ln in lines:
        if re.search(r"(experience|employment|work history)", ln, re.I):
            if current:
                blocks.append({"raw": " ".join(current[:8])})
                current = []
            continue
        current.append(ln)
        if len(current) > 12:
            blocks.append({"raw": " ".join(current[:8])})
            current = current[8:]
    if current:
        blocks.append({"raw": " ".join(current[:8])})
    return blocks[:5]


def _heuristic_education(text: str) -> list[dict[str, Any]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    edu: list[dict[str, Any]] = []
    capture = False
    buf: list[str] = []
    for ln in lines:
        if re.search(r"(education|academic)", ln, re.I):
            capture = True
            continue
        if capture:
            if re.search(r"(experience|skills|reference)", ln, re.I):
                break
            buf.append(ln)
            if len(buf) >= 6:
                edu.append({"raw": " ".join(buf)})
                buf = []
    if buf:
        edu.append({"raw": " ".join(buf)})
    return edu[:4]


def parse_resume_bytes(filename: str, data: bytes) -> dict[str, Any]:
    settings = get_settings()
    lower = filename.lower()
    if lower.endswith(".pdf"):
        text = extract_pdf_text(data)
    elif lower.endswith(".docx"):
        text = extract_docx_text(data)
    else:
        raise ValueError("Unsupported file type; use PDF or DOCX")

    structured: dict[str, Any] = {
        "full_text": text[:200_000],
        "skills_guess": _heuristic_skills(text),
        "experience_guess": _heuristic_experience(text),
        "education_guess": _heuristic_education(text),
    }

    if settings.cv_parser_mode == "spacy":
        structured["spacy"] = _optional_spacy_entities(text[:50_000])

    if settings.affinda_api_key:
        structured["affinda"] = "not_implemented_in_repo_stub"

    return structured


def _optional_spacy_entities(text: str) -> dict[str, Any]:
    try:
        import spacy  # type: ignore

        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        return {"ents": [(e.text, e.label_) for e in doc.ents[:50]]}
    except Exception as exc:  # pragma: no cover - optional path
        return {"error": str(exc)}
