from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import asyncio
import random
from sqlalchemy import update
from sqlalchemy.future import select

# database 모듈에서 비동기 세션 팩토리 가져오기
# lifespan에서 생성된 scheduler가 DB 세션을 직접 받기는 어려우므로,
# 스케줄러 작업 내에서 세션을 생성하는 방식 사용
try:
    from .database import AsyncSessionFactory, engine as db_engine
    from .models import User
except ImportError:
    # 스케줄러만 단독 실행하거나 경로 문제 시 예외 처리
    print("Warning: Could not import database components in scheduler. DB operations will fail.")
    AsyncSessionFactory = None
    db_engine = None
    User = None

class MatchingScheduler:
    def __init__(self):
        # wait_seconds=0 추가 (즉시 종료되도록)
        self.scheduler = AsyncIOScheduler()
        self._running = False # 실행 상태 플래그 추가
    
    def start(self):
        if self._running:
            print("Scheduler is already running.")
            return

        # 매일 자정에 초대장 카운트 초기화
        self.scheduler.add_job(
            self.reset_daily_invitation_counts,
            CronTrigger(hour=0, minute=0)
            # CronTrigger(second=0) # 테스트용: 매 분 실행
        )
        
        # 매시간 사용자 가시성 업데이트
        self.scheduler.add_job(
            self.update_user_visibility,
            CronTrigger(minute=0)
            # CronTrigger(second=30) # 테스트용: 30초마다 실행
        )
        
        try:
            print("Starting scheduler...")
            self.scheduler.start()
            self._running = True
            print("Scheduler started successfully.")
        except Exception as e:
            print(f"Error starting scheduler: {e}")
    
    async def shutdown(self, wait=True):
        if self._running and self.scheduler.running:
            print("Shutting down scheduler...")
            # wait=False로 설정하여 즉시 종료 시도
            self.scheduler.shutdown(wait=wait)
            self._running = False
            print("Scheduler shut down.")
        else:
            print("Scheduler is not running or already shut down.")
    
    async def reset_daily_invitation_counts(self):
        # TODO: DB 구현 후 실제 초기화
        print(f"[{datetime.now()}] 스케줄러 작업: 초대장 카운트 초기화")
    
    async def update_user_visibility(self):
        """매시간 실행: 사용자별 최근 매칭 수를 기반으로 visibility_score 업데이트 (현재는 임시 로직)"""
        print(f"[{datetime.now()}] 스케줄러 작업: 사용자 가시성 업데이트 시작")
        if not AsyncSessionFactory or not User:
            print("Database components not available. Skipping visibility update.")
            return

        async with AsyncSessionFactory() as session:
            async with session.begin(): # 트랜잭션 시작
                try:
                    # TODO: MongoDB 연동 후 실제 최근 매칭 수 집계 로직 구현
                    # 예: 지난 1시간 또는 24시간 동안의 매칭 성공/요청 수 집계
                    # user_match_counts = await get_recent_match_counts_from_mongodb(timedelta(hours=24))

                    # 현재: 임시 로직 - 모든 유저의 visibility_score를 랜덤하게 약간 조정
                    stmt = select(User.user_id)
                    result = await session.execute(stmt)
                    all_user_ids = result.scalars().all()

                    updated_count = 0
                    for user_id in all_user_ids:
                        # 임시: 랜덤 패널티 적용 (0.5 ~ 1.0 사이)
                        # 실제로는 user_match_counts[user_id] 같은 값을 사용
                        recent_count_mock = random.randint(0, 5) # 0~5 사이 임의의 매칭 수
                        penalty_factor = 0.1
                        new_score = max(0.1, 1.0 / (1 + recent_count_mock * penalty_factor)) # 최소 0.1 보장

                        update_stmt = (
                            update(User)
                            .where(User.user_id == user_id)
                            .values(visibility_score=new_score)
                        )
                        await session.execute(update_stmt)
                        updated_count += 1

                    print(f"Visibility score updated for {updated_count} users.")
                    # await session.commit() # session.begin() 사용 시 자동 커밋/롤백
                except Exception as e:
                    print(f"Error updating visibility scores: {e}")
                    # await session.rollback() # session.begin() 사용 시 자동 롤백
                    # 필요시 에러 로깅 추가

        print(f"[{datetime.now()}] 스케줄러 작업: 사용자 가시성 업데이트 완료") 