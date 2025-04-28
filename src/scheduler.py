from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

class MatchingScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        # 매일 자정에 초대장 카운트 초기화
        self.scheduler.add_job(
            self.reset_daily_invitation_counts,
            CronTrigger(hour=0, minute=0)
        )
        
        # 매시간 사용자 가시성 업데이트
        self.scheduler.add_job(
            self.update_user_visibility,
            CronTrigger(minute=0)
        )
        
        self.scheduler.start()
    
    async def reset_daily_invitation_counts(self):
        # TODO: DB 구현 후 실제 초기화
        print(f"[{datetime.now()}] 초대장 카운트 초기화")
    
    async def update_user_visibility(self):
        # TODO: DB 구현 후 실제 업데이트
        print(f"[{datetime.now()}] 사용자 가시성 업데이트") 