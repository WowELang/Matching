import os # os 추가
# from dotenv import load_dotenv # dotenv 추가

# 애플리케이션 시작점 바로 아래, 다른 임포트보다 먼저 .env 파일 로드
# load_dotenv() # 주석 처리 또는 삭제

from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Optional, Dict, Set
import uvicorn
import numpy as np
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.database import get_db_session
import src.models as models
from src.schemas import UserSchema, UserTypeEnumPydantic
import json
import enum
from .scheduler import MatchingScheduler
import contextlib
import asyncio
import logging # 로깅 추가
import fasttext # fasttext 임포트 복원
# from transformers import AutoTokenizer, AutoModel # transformers 임포트 주석처리
from .utils import get_profile_vector, calculate_cosine_similarity # 유틸리티 함수 임포트

# --- Logging 설정 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lifespan 이벤트 핸들러 --- #
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")

    # FastText 모델 로드 (fasttext 라이브러리 사용)
    model_path = "embedding_models/ko.bin"
    if os.path.exists(model_path):
        try:
            logger.info(f"Loading FastText model from {model_path}...")
            app.state.ft_model = fasttext.load_model(model_path)
            logger.info("FastText model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load FastText model: {e}", exc_info=True)
            app.state.ft_model = None # 로딩 실패 시 None으로 설정
    else:
        logger.warning(f"FastText model file not found at {model_path}. Embedding features will be disabled.")
        app.state.ft_model = None

    # # klue/roberta-small transformers 모델 로드 (주석처리)
    # try:
    #     logger.info("Loading klue/roberta-small model and tokenizer...")
    #     tokenizer = AutoTokenizer.from_pretrained("klue/roberta-small")
    #     model = AutoModel.from_pretrained("klue/roberta-small")
    #     app.state.ft_model = (tokenizer, model)
    #     logger.info("klue/roberta-small loaded successfully.")
    # except Exception as e:
    #     logger.error(f"Failed to load klue/roberta-small: {e}", exc_info=True)
    #     app.state.ft_model = None

    # 스케줄러 인스턴스 생성 및 시작
    scheduler = MatchingScheduler()
    try:
        scheduler.start()
        # 스케줄러 인스턴스를 앱 상태에 저장 (선택 사항, 필요시 다른 곳에서 접근)
        app.state.scheduler = scheduler
        logger.info("Scheduler started successfully.")
        yield # 애플리케이션 실행
    finally:
        # 애플리케이션 종료 시 실행
        logger.info("Shutting down application lifespan...")
        if hasattr(app.state, 'scheduler'):
            await app.state.scheduler.shutdown()
            logger.info("Scheduler shut down.")
        else:
            logger.warning("Scheduler instance not found in app state during shutdown.")
        # 모델 메모리 해제 (선택적, Python GC에 맡길 수도 있음)
        if hasattr(app.state, 'ft_model') and app.state.ft_model is not None:
            del app.state.ft_model # 참조 제거
            logger.info("FastText model unloaded.")
            # 명시적으로 메모리 정리가 필요하면 추가적인 라이브러리 사용 고려 (예: gc.collect())

# --- FastAPI 앱 생성 (lifespan 인자 추가) --- #
app = FastAPI(title="Wowelang Matching API", lifespan=lifespan)

# --- Helper 함수: DB 결과 -> Pydantic UserSchema 변환 ---
def parse_interest(interest_str: Optional[str]) -> List[str]:
    if not interest_str: return []
    try: return json.loads(interest_str)
    except json.JSONDecodeError: return []
    except: return []

def create_pydantic_user(db_user: 'models.User') -> Optional[UserSchema]:
    if not db_user: return None

    # User.interests 관계를 통해 Interest 객체 리스트를 가져오고, 각 객체의 interest_name을 추출
    interests_list = [interest.interest_name for interest in db_user.interests if interest and interest.interest_name]

    user_data = {
        "user_id": db_user.user_id,
        "name": db_user.name,
        "usertype": UserTypeEnumPydantic.NATIVE if db_user.usertype == models.UserTypeEnumDB.NATIVE else UserTypeEnumPydantic.FOREIGN,
        "major": db_user.major,
        "interest": interests_list,
        "isOn": bool(db_user.is_on),
    }
    if db_user.usertype == models.UserTypeEnumDB.NATIVE and db_user.korean_attribute:
        user_data["reputation"] = db_user.korean_attribute.reputation
        user_data["country"] = "한국"
    elif db_user.usertype == models.UserTypeEnumDB.FOREIGN and db_user.foreign_attribute:
        user_data["country"] = db_user.foreign_attribute.country
        user_data["reputation"] = 0
    else:
        user_data["reputation"] = 0
        user_data["country"] = "한국" if db_user.usertype == models.UserTypeEnumDB.NATIVE else (db_user.foreign_attribute.country if db_user.usertype == models.UserTypeEnumDB.FOREIGN and db_user.foreign_attribute else None)

    try:
        return UserSchema(**user_data)
    except Exception as e:
        print(f"Pydantic validation error for user {db_user.user_id}: {e}")
        return None
# --- Helper 끝 ---

# --- 협업필터링 클래스 --- (향후 MongoDB 연동 시 수정)
class CollaborativeFiltering:
    def __init__(self):
        self.user_matching_history: Dict[int, Set[int]] = defaultdict(set)
        self.user_interests: Dict[int, Set[str]] = defaultdict(set)

    def add_matching_history(self, user1_id: int, user2_id: int, status: str):
        if status == 'ACCEPTED':
            self.user_matching_history[user1_id].add(user2_id)
            self.user_matching_history[user2_id].add(user1_id)

    def add_user_interests(self, user_id: int, interests: List[str]):
        self.user_interests[user_id] = set(interests)

    def calculate_similarity(self, user1_id: int, user2_id: int) -> float:
        user1_matches = self.user_matching_history.get(user1_id, set())
        user2_matches = self.user_matching_history.get(user2_id, set())
        history_similarity = 0.0
        if user1_matches and user2_matches:
            intersection = len(user1_matches & user2_matches)
            union = len(user1_matches | user2_matches)
            history_similarity = intersection / union if union > 0 else 0.0

        user1_interests = self.user_interests.get(user1_id, set())
        user2_interests = self.user_interests.get(user2_id, set())
        interest_similarity_cf = 0.0 # 변수명 변경 (아래 계산과 구분)
        if user1_interests and user2_interests:
            intersection = len(user1_interests & user2_interests)
            union = len(user1_interests | user2_interests)
            interest_similarity_cf = intersection / union if union > 0 else 0.0

        weights = {'history': 0.6, 'interest': 0.4}
        return (history_similarity * weights['history'] + interest_similarity_cf * weights['interest'])
# --- 협업필터링 끝 ---

# --- 추천 점수 계산기 --- (수정됨)
class MatchingScoreCalculator:
    # __init__ 타입 힌트 변경 (Optional[gensim...] -> Optional[fasttext.FastText._FastText])
    def __init__(self, cf: CollaborativeFiltering, ft_model: Optional['fasttext.FastText._FastText']):
        self.cf = cf
        self.ft_model = ft_model # FastText 모델 저장

    def calculate_score(self, user: UserSchema, target: UserSchema) -> float:
        # 1. 관심사 + 학과 임베딩 기반 유사도 계산 (수정됨)
        if self.ft_model:
            # get_profile_vector 함수는 이제 fasttext 모델 객체를 받음
            user_vector = get_profile_vector(self.ft_model, user.interest or [], user.major)
            target_vector = get_profile_vector(self.ft_model, target.interest or [], target.major)
            interest_similarity = calculate_cosine_similarity(user_vector, target_vector)
        else:
            interest_similarity = 0.0
            logger.warning("FastText model not available, using 0 for interest similarity.")

        # 2. 평판 점수 & 가중치 설정 (Target 타입에 따라 분기)
        # target.userType은 이제 NATIVE 또는 FOREIGN 값임
        if target.userType == UserTypeEnumPydantic.NATIVE: # API 기준 NATIVE (DB에서는 KOREAN)
            reputation_score = min((target.reputation or 0) / 100.0, 1.0)
            weights = {'interest': 0.5, 'reputation': 0.2, 'cf': 0.3}
        elif target.userType == UserTypeEnumPydantic.FOREIGN:
            reputation_score = 0.0
            weights = {'interest': 0.6, 'reputation': 0.0, 'cf': 0.4}
        else:
            logger.warning(f"Unknown target user type: {target.userType}")
            reputation_score = 0.0
            weights = {'interest': 0.6, 'reputation': 0.0, 'cf': 0.4}

        # 3. 협업필터링 점수 - 이전과 동일
        cf_score = self.cf.calculate_similarity(user.userId, target.userId)

        # 4. 최종 점수 계산 (수정된 가중치 사용)
        final_score = (
            interest_similarity * weights['interest'] +
            reputation_score * weights['reputation'] +
            cf_score * weights['cf']
        )
        return max(0.0, min(final_score, 1.0))
# --- 추천 점수 계산기 끝 ---

# --- 매칭 서비스 --- (DB 조회 및 isOn 필터링 적용)
class MatchingService:
    # __init__ 타입 힌트 변경
    def __init__(self, ft_model: Optional['fasttext.FastText._FastText']):
        self.cf = CollaborativeFiltering() # 매번 새로 생성 (DB 연동 시 수정 필요)
        # ft_model을 MatchingScoreCalculator에 전달
        self.score_calculator = MatchingScoreCalculator(self.cf, ft_model)

    async def _get_user(self, userId: int, db: AsyncSession) -> Optional[UserSchema]:
        # select() 안에 특정 컬럼을 명시하지 않고, User 모델 전체를 선택하도록 변경
        stmt = (
            select(models.User) # User 모델 객체 전체를 선택
            .options(
                selectinload(models.User.korean_attribute),
                selectinload(models.User.foreign_attribute),
                selectinload(models.User.interests)  # User의 interests를 Eager Loading
            )
            .where(models.User.user_id == userId)
        )
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
        return create_pydantic_user(db_user)

    async def _get_opposite_users(self, userId: int, userType: UserTypeEnumPydantic, db: AsyncSession) -> List[UserSchema]:
        db_user_model_type = models.UserTypeEnumDB.NATIVE if userType == UserTypeEnumPydantic.NATIVE else models.UserTypeEnumDB.FOREIGN
        db_opposite_model_type = models.UserTypeEnumDB.FOREIGN if db_user_model_type == models.UserTypeEnumDB.NATIVE else models.UserTypeEnumDB.NATIVE

        stmt = (
            select(models.User)
            .options(
                selectinload(models.User.korean_attribute),
                selectinload(models.User.foreign_attribute),
                selectinload(models.User.interests)
            )
            .where(
                models.User.usertype == db_opposite_model_type,
                models.User.user_id != userId,
                models.User.is_on == True
            )
        )
        result = await db.execute(stmt)
        db_users = result.scalars().all()
        return [p_user for db_user in db_users if (p_user := create_pydantic_user(db_user)) is not None]

    async def get_matching_list(self, userId: int, userType: UserTypeEnumPydantic, db: AsyncSession) -> List[dict]:
        user_pydantic = await self._get_user(userId, db)
        if not user_pydantic:
            raise HTTPException(status_code=404, detail=f"User with ID {userId} not found")

        # 요청한 유저의 userType (NATIVE 또는 FOREIGN)을 그대로 사용
        candidates_pydantic = await self._get_opposite_users(userId, userType, db)
        if not candidates_pydantic:
            return []

        # 협업 필터링 데이터 로딩 (예시)
        # for u in [user_pydantic] + candidates_pydantic:
        #     if u and u.interest:
        #        self.cf.add_user_interests(u.userId, u.interest)

        result = []
        for target in candidates_pydantic:
            base_score = self.score_calculator.calculate_score(user_pydantic, target)
            result.append({
                'userId': target.userId,
                'username': target.username, # target.name -> target.username 으로 수정
                'userType': target.userType.value,
                'major': target.major,
                'country': target.country,
                'interest': target.interest,
                'reputation': target.reputation,
                'isOn': target.isOn,
                'matchingScore': round(base_score, 4)
            })

        result.sort(key=lambda x: x['matchingScore'], reverse=True)
        return result

    # --- 매칭 생성/응답 관련 함수 (MongoDB 연동 시 구현) --- #
    # async def save_matching_history(self, nativeUserId: int, foreignUserId: int, status: str):
    #     # MongoDB에 매칭 정보 저장/업데이트 로직
    #     print(f"TODO: Save matching history to MongoDB - {nativeUserId} vs {foreignUserId}, Status: {status}")
    #     # 협업 필터링 데이터 업데이트 (현재는 메모리)
    #     self.cf.add_matching_history(nativeUserId, foreignUserId, status)
    #     pass
# --- 매칭 서비스 끝 ---

# --- API 엔드포인트 --- #
@app.get('/api/matching/list')
async def get_matching_list_endpoint(
    request: Request, # Request 객체 추가
    userId: int,
    userType: UserTypeEnumPydantic, # Pydantic Enum 타입으로 받음 (NATIVE 또는 FOREIGN)
    db: AsyncSession = Depends(get_db_session)
):
    """주어진 유저 ID와 타입 기준으로 매칭 리스트 반환"""
    ft_model = request.app.state.ft_model if hasattr(request.app.state, 'ft_model') else None
    service = MatchingService(ft_model=ft_model)
    try:
        # userType (NATIVE 또는 FOREIGN)을 그대로 서비스 함수에 전달
        return await service.get_matching_list(userId, userType, db)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error in get_matching_list_endpoint: {e}", exc_info=True) # 로깅 개선
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- 매칭 생성/응답 엔드포인트 (MongoDB 연동 후 구현) --- #
# @app.post('/api/matching/invite')
# async def send_invite(nativeUserId: int, foreignUserId: int):
#     service = MatchingService()
#     await service.save_matching_history(nativeUserId, foreignUserId, 'PENDING')
#     return {"status": "PENDING"}

# @app.put('/api/matching/invite/{matchId}/respond')
# async def respond_invite(matchId: int, nativeUserId: int, foreignUserId: int, status: str):
#     # status 유효성 검증 필요 ('ACCEPTED', 'REJECTED')
#     service = MatchingService()
#     await service.save_matching_history(nativeUserId, foreignUserId, status)
#     return {"status": status}
# --- API 엔드포인트 끝 --- #

# --- 서버 실행 (main 블록) --- #
# 이 블록은 이제 uvicorn 명령어를 직접 사용할 것이므로, 없어도 무방합니다.
# 만약 남겨둔다면, 실행 시 중복 실행되지 않도록 주의해야 합니다.
# if __name__ == "__main__":
#     print("Running from main block - This might not be intended when using lifespan with uvicorn command.")
#     # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # 중복 실행될 수 있음 