    # src/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging # logging 추가
# from dotenv import load_dotenv # 주석 처리

logger = logging.getLogger(__name__)

# 프로젝트 루트의 .env 파일 로드 시도 (주석 처리)
# dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path=dotenv_path)
# else:
#     load_dotenv() # 시스템 환경 변수 또는 기본 위치에서 로드 (주석 처리)

# DATABASE_URL 환경 변수를 직접 사용
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.critical("CRITICAL: DATABASE_URL environment variable is not set!")
    # 실제 운영 환경에서는 에러를 발생시키거나 기본값 사용 등의 처리가 필요
    # exit(1)
    # 여기서는 일단 None으로 진행되어 연결 시 에러 발생

# DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4" # 이전 방식 주석 처리

engine = create_async_engine(DATABASE_URL, echo=True, pool_recycle=3600) # echo=True는 SQL 로깅, pool_recycle 추가
AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Dependency로 사용할 비동기 세션 getter
async def get_db_session() -> AsyncSession: # 타입 힌트 명시
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            print(f"Session commit failed: {e}") # 에러 로깅
            await session.rollback()
            raise # 에러 재발생
        finally:
            await session.close()