from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Set
from datetime import datetime
import uvicorn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

app = FastAPI(title="Wowelang Matching API")

# ERD 기반 모델/DTO 정의
class User(BaseModel):
    userId: int
    username: str
    userType: str  # 'KOREAN' or 'FOREIGN'
    major: Optional[str]
    country: Optional[str]
    interest: List[str]  # 콤마로 구분된 문자열을 리스트로 변환
    reputation: Optional[int] = 0
    foxRate: Optional[int] = 0

class UserMatching(BaseModel):
    matchId: int
    nativeUserId: int
    foreignUserId: int
    status: str  # 'PENDING', 'ACCEPTED', 'REJECTED'
    created_at: str
    updated_at: str

# 협업필터링 클래스
class CollaborativeFiltering:
    def __init__(self):
        self.user_matching_history: Dict[int, Set[int]] = defaultdict(set)  # userId별 ACCEPTED 상대 userId set
        self.user_interests: Dict[int, Set[str]] = defaultdict(set)         # userId별 관심사 set

    def add_matching_history(self, user1_id: int, user2_id: int, status: str):
        if status == 'ACCEPTED':
            self.user_matching_history[user1_id].add(user2_id)
            self.user_matching_history[user2_id].add(user1_id)

    def add_user_interests(self, user_id: int, interests: List[str]):
        self.user_interests[user_id] = set(interests)

    def calculate_similarity(self, user1_id: int, user2_id: int) -> float:
        # 매칭 히스토리 기반 유사도
        user1_matches = self.user_matching_history.get(user1_id, set())
        user2_matches = self.user_matching_history.get(user2_id, set())
        if not user1_matches or not user2_matches:
            history_similarity = 0.0
        else:
            intersection = len(user1_matches & user2_matches)
            union = len(user1_matches | user2_matches)
            history_similarity = intersection / union if union > 0 else 0.0
        # 관심사 기반 유사도
        user1_interests = self.user_interests.get(user1_id, set())
        user2_interests = self.user_interests.get(user2_id, set())
        if not user1_interests or not user2_interests:
            interest_similarity = 0.0
        else:
            intersection = len(user1_interests & user2_interests)
            union = len(user1_interests | user2_interests)
            interest_similarity = intersection / union if union > 0 else 0.0
        # 가중치 적용
        weights = {'history': 0.6, 'interest': 0.4}
        return (history_similarity * weights['history'] + interest_similarity * weights['interest'])

# 추천 점수 계산기
class MatchingScoreCalculator:
    def __init__(self, cf: CollaborativeFiltering):
        self.cf = cf

    def calculate_score(self, user: User, target: User) -> float:
        # 1. 관심사 유사도 (코사인 유사도)
        all_interests = list(set(user.interest + target.interest))
        user_vec = [1 if i in user.interest else 0 for i in all_interests]
        target_vec = [1 if i in target.interest else 0 for i in all_interests]
        interest_similarity = cosine_similarity([user_vec], [target_vec])[0][0] if all_interests else 0.0
        # 2. 평판 점수 정규화
        reputation_score = min((target.reputation or 0) / 100.0, 1.0)
        # 3. 신고 횟수 점수 (신고 많을수록 감점)
        fox_score = max(1.0 - (target.foxRate or 0) / 10.0, 0.0)
        # 4. 협업필터링 점수
        cf_score = self.cf.calculate_similarity(user.userId, target.userId)
        # 5. 가중치 적용
        weights = {'interest': 0.3, 'reputation': 0.2, 'fox': 0.1, 'cf': 0.4}
        return (
            interest_similarity * weights['interest'] +
            reputation_score * weights['reputation'] +
            fox_score * weights['fox'] +
            cf_score * weights['cf']
        )

# 매칭 서비스
class MatchingService:
    def __init__(self):
        self.cf = CollaborativeFiltering()
        self.score_calculator = MatchingScoreCalculator(self.cf)

    async def get_matching_list(self, userId: int, userType: str) -> List[dict]:
        # 1. DB에서 userType이 반대인 유저만 조회 (TODO)
        candidates = await self._get_opposite_users(userId, userType)
        user = await self._get_user(userId)
        # 2. 관심사, 평판, 신고, 협업필터링 점수 계산
        result = []
        for target in candidates:
            score = self.score_calculator.calculate_score(user, target)
            result.append({
                'userId': target.userId,
                'username': target.username,
                'userType': target.userType,
                'major': target.major,
                'country': target.country,
                'interest': target.interest,
                'reputation': target.reputation,
                'foxRate': target.foxRate,
                'matchingScore': score
            })
        # 3. 추천 점수 높은 순 정렬
        result.sort(key=lambda x: x['matchingScore'], reverse=True)
        return result

    async def save_matching_history(self, nativeUserId: int, foreignUserId: int, status: str):
        # Untitled(유저매칭) 테이블에 저장 (TODO: 실제 DB 연동)
        self.cf.add_matching_history(nativeUserId, foreignUserId, status)

    async def _get_opposite_users(self, userId: int, userType: str) -> List[User]:
        # TODO: 실제 DB에서 userType이 반대인 유저만 조회
        # 예시 데이터
        if userType == 'KOREAN':
            return [User(userId=2, username='유학생A', userType='FOREIGN', major='경영', country='중국', interest=['음악','여행'], reputation=80, foxRate=1)]
        else:
            return [User(userId=1, username='한국인A', userType='KOREAN', major='컴공', country='한국', interest=['프로그래밍','음악'], reputation=90, foxRate=0)]

    async def _get_user(self, userId: int) -> User:
        # TODO: 실제 DB에서 userId로 유저 조회
        # 예시 데이터
        if userId == 1:
            return User(userId=1, username='한국인A', userType='KOREAN', major='컴공', country='한국', interest=['프로그래밍','음악'], reputation=90, foxRate=0)
        else:
            return User(userId=2, username='유학생A', userType='FOREIGN', major='경영', country='중국', interest=['음악','여행'], reputation=80, foxRate=1)

# API 엔드포인트
@app.get('/api/matching/list')
async def get_matching_list(userId: int, userType: str):
    service = MatchingService()
    return await service.get_matching_list(userId, userType)

@app.post('/api/matching/invite')
async def send_invite(nativeUserId: int, foreignUserId: int):
    service = MatchingService()
    await service.save_matching_history(nativeUserId, foreignUserId, 'PENDING')
    return {"status": "PENDING"}

@app.put('/api/matching/invite/{matchId}/respond')
async def respond_invite(matchId: int, nativeUserId: int, foreignUserId: int, status: str):
    service = MatchingService()
    await service.save_matching_history(nativeUserId, foreignUserId, status)
    return {"status": status}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 