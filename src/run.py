import uvicorn
from main import app
from scheduler import MatchingScheduler

if __name__ == "__main__":
    # 스케줄러 시작
    scheduler = MatchingScheduler()
    scheduler.start()
    
    # FastAPI 서버 시작
    uvicorn.run(app, host="0.0.0.0", port=8000) 