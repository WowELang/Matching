import numpy as np
from typing import List, Optional
import fasttext

def get_profile_vector(
    model: Optional['fasttext.FastText._FastText'],
    interests: List[str],
    major: Optional[str]
) -> np.ndarray:
    """주어진 관심사 리스트와 전공으로 프로필 벡터 생성 (FastText 기반)"""
    if not model:
        return np.zeros(300)  # FastText 벡터 차원 기본값

    dim = model.get_dimension()
    vectors = []

    # 1. 관심사 벡터 추가
    for interest in interests:
        if interest:
            try:
                vec = model.get_word_vector(interest.strip())
                vectors.append(vec)
            except Exception:
                pass

    # 2. 전공 벡터 추가
    if major:
        try:
            vec = model.get_word_vector(major.strip())
            vectors.append(vec)
        except Exception:
            pass

    # 3. 벡터 평균 계산
    if not vectors:
        return np.zeros(dim)
    profile_vector = np.mean(vectors, axis=0)
    return profile_vector

def calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """두 벡터 간의 코사인 유사도 계산"""
    # 제로 벡터 체크 (분모가 0이 되는 것 방지)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2) 