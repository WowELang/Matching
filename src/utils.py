import numpy as np
from typing import List, Optional
import fasttext # fasttext 임포트

def get_profile_vector(
    model: Optional['fasttext.FastText._FastText'], # 타입 힌트 변경
    interests: List[str],
    major: Optional[str]
) -> np.ndarray:
    """주어진 관심사 리스트와 전공으로 프로필 벡터 생성"""
    if not model:
        # 모델 로딩 실패 시 0 벡터 반환 (또는 다른 기본값)
        # fasttext 모델의 기본 벡터 크기는 get_dimension()으로 얻을 수 있음
        # 하지만 모델이 None이면 알 수 없으므로, 일반적인 300 차원으로 가정하거나 에러 처리
        # 여기서는 300차원 0 벡터 반환
        return np.zeros(300)

    dim = model.get_dimension() # 모델 벡터 차원 얻기
    vectors = []

    # 1. 관심사 벡터 추가
    for interest in interests:
        if interest:
            try:
                # fasttext 모델에서 단어 벡터 조회: model.get_word_vector(단어)
                vec = model.get_word_vector(interest.strip())
                vectors.append(vec)
            except KeyError:
                # 모델에 없는 단어는 건너뛰기
                pass

    # 2. 전공 벡터 추가
    if major:
        try:
            vec = model.get_word_vector(major.strip())
            vectors.append(vec)
        except KeyError:
            pass

    # 3. 벡터 평균 계산
    if not vectors:
        # 유효한 벡터가 하나도 없으면 0 벡터 반환
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