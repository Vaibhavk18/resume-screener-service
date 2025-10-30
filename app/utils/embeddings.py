from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def similarity_score_0_100(a: np.ndarray, b: np.ndarray) -> int:
    sim = cosine_similarity(a, b)
    sim = max(-1.0, min(1.0, sim))
    return int(round((sim + 1.0) * 50)) 