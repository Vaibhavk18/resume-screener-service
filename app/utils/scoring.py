from typing import Dict, List, Tuple

import numpy as np

from app.utils.embeddings import embed_texts, similarity_score_0_100
from app.utils.nlp import extract_skills, NLP
import re


def jaccard_similarity(a: List[str], b: List[str]) -> float:
    set_a, set_b = set([x.lower() for x in a]), set([x.lower() for x in b])
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def semantic_skill_match(resume_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str]]:
    # Try to match semantically if exact match fails; threshold tuned lightly
    if not resume_skills or not jd_skills:
        return [], jd_skills
    texts = [*resume_skills, *jd_skills]
    vectors = embed_texts(texts)
    r_vecs = vectors[: len(resume_skills)]
    j_vecs = vectors[len(resume_skills) :]
    matched = set()
    for j_idx, j_skill in enumerate(jd_skills):
        sims = np.dot(r_vecs, j_vecs[j_idx])  # cosine since normalized
        if sims.max(initial=-1.0) >= 0.6:
            matched.add(j_skill)
    matched_list = sorted(matched, key=lambda s: s.lower())
    missing_list = sorted([s for s in jd_skills if s not in matched], key=lambda s: s.lower())
    return matched_list, missing_list


def split_sentences(text: str) -> List[str]:
    # Prefer spaCy if available for better sentence boundaries
    if NLP is not None:
        try:
            if "senter" not in NLP.pipe_names and "sentencizer" not in NLP.pipe_names:
                NLP.add_pipe("sentencizer")
            doc = NLP(text)
            return [s.text.strip() for s in getattr(doc, "sents", []) if s.text.strip()]
        except Exception:
            pass
    # Fallback regex split on punctuation followed by whitespace/newline
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p and p.strip()]


def score_resume_against_jd(resume_text: str, jd_text: str) -> Dict:
    # Embedding similarity score
    vecs = embed_texts([resume_text, jd_text])
    score = similarity_score_0_100(vecs[0], vecs[1])

    # Skill overlap
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    exact_matched = sorted(set(resume_skills) & set(jd_skills), key=lambda s: s.lower())
    exact_missing = sorted(set(jd_skills) - set(exact_matched), key=lambda s: s.lower())

    if exact_missing:
        sem_matched, sem_missing = semantic_skill_match(resume_skills, jd_skills)
        matched_skills = sorted(set(exact_matched) | set(sem_matched), key=lambda s: s.lower())
        missing_skills = [s for s in jd_skills if s not in matched_skills]
    else:
        matched_skills = exact_matched
        missing_skills = exact_missing

    # Explanation snippets: top sentences in resume closest to JD
    resume_sentences = split_sentences(resume_text)[:50]
    if not resume_sentences:
        explanations = []
    else:
        all_texts = [jd_text] + resume_sentences
        all_vecs = embed_texts(all_texts)
        jd_vec = all_vecs[0]
        res_vecs = all_vecs[1:]
        sims = np.dot(res_vecs, jd_vec)
        top_idx = np.argsort(-sims)[:5]
        explanations = [resume_sentences[i] for i in top_idx]

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "explanations": explanations,
    } 