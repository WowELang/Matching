import os
import json
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, exc

print("--- Script Starting ---") # 시작 로그 추가

# mock 데이터 생성 함수 import
try:
    print("Importing mock_data_generator...")
    from mock_data_generator import generate_mock_users
    print("Import successful.")
except ImportError:
    print("Error: Could not import generate_mock_users from mock_data_generator.")
    print("Ensure mock_data_generator.py exists in the same directory (DB_test/).")
    sys.exit(1)

# .env 파일 로드
print("Loading .env file...")
# 스크립트 위치(DB_test)의 상위 디렉토리(프로젝트 루트)에서 .env 찾기
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')

if os.path.exists(dotenv_path):
    loaded = load_dotenv(dotenv_path=dotenv_path, verbose=True) # verbose=True 추가
    print(f".env file loaded from {dotenv_path}: {loaded}")
else:
    print(f"Warning: .env file not found at {dotenv_path}. Trying system environment.")
    loaded = load_dotenv(verbose=True)
    print(f"load_dotenv result (system env): {loaded}")

# DB 연결 정보 로드 및 확인
print("Loading DB environment variables...")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

print(f"DB_USER: {'Set' if DB_USER else 'Not Set'}")
print(f"DB_PASSWORD: {'Set' if DB_PASSWORD else 'Not Set'}")
print(f"DB_HOST: {'Set' if DB_HOST else 'Not Set'}")
print(f"DB_PORT: {'Set' if DB_PORT else 'Not Set'}")
print(f"DB_NAME: {'Set' if DB_NAME else 'Not Set'}")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    print("Error: Database environment variables missing.")
    sys.exit(1)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
print(f"Database URL constructed: {DATABASE_URL.replace(DB_PASSWORD, '********') if DB_PASSWORD else DATABASE_URL}") # 비밀번호 가리기

try:
    engine = create_engine(DATABASE_URL, echo=False)
    mock_users_to_insert = generate_mock_users(25, 25)
    print(f"Generated {len(mock_users_to_insert)} mock users.")

    with engine.connect() as connection:
        # --- 트랜잭션 1: 데이터 삭제 --- #
        delete_transaction = connection.begin()
        try:
            print("Clearing existing data...")
            connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            connection.execute(text("DELETE FROM foreign_tutee_attribute"))
            connection.execute(text("DELETE FROM korean_tutor_attribute"))
            connection.execute(text("DELETE FROM user"))
            connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            delete_transaction.commit()
            print("Existing data cleared and committed.")
        except exc.SQLAlchemyError as e:
            print(f"Error during data clearing: {e}")
            delete_transaction.rollback()
            print("Data clearing rolled back.")
            sys.exit(1) # 데이터 삭제 실패 시 중단
        except Exception as e:
            print(f"Unexpected error during data clearing: {e}")
            delete_transaction.rollback()
            print("Data clearing rolled back.")
            sys.exit(1)

        # --- 트랜잭션 2: 데이터 삽입 --- #
        insert_transaction = connection.begin()
        try:
            print("Inserting new mock data (with visibility_score=1.0)...")
            inserted_count = 0
            for user_data in mock_users_to_insert:
                try:
                    # interest 리스트를 JSON 문자열로 변환
                    interest_str = json.dumps(user_data.get('interest', []), ensure_ascii=False)

                    # 1. user 테이블 삽입 (visibility_score 추가)
                    user_insert_sql = text("""
                        INSERT INTO user (user_id, login_id, email, password, name, birthday, major, gender, usertype, is_email_verified, interest, isOn, visibility_score)
                        VALUES (:userId, :login_id, :email, :password, :name, :birthday, :major, :gender, :usertype, :is_email_verified, :interest, :isOn, :visibility_score)
                    """)
                    user_params = {
                        "userId": user_data['userId'],
                        "login_id": user_data['login_id'],
                        "email": user_data['email'],
                        "password": user_data['password'],
                        "name": user_data['username'],
                        "birthday": user_data['birthday'],
                        "major": user_data['major'],
                        "gender": user_data['gender'],
                        "usertype": user_data['userType'],
                        "is_email_verified": 1,
                        "interest": interest_str,
                        "isOn": 1 if user_data['isOn'] else 0,
                        "visibility_score": 1.0 # <-- 기본값 1.0으로 설정
                    }
                    connection.execute(user_insert_sql, user_params)

                    # 2. 속성 테이블 삽입 (이하 생략, 이전 코드와 동일)
                    # ... (if user_data['userType'] == 'KOREAN': ...) ...
                    # ... (elif user_data['userType'] == 'FOREIGN': ...) ...

                    inserted_count += 1
                except exc.SQLAlchemyError as insert_error:
                    print(f"Error inserting user ID {user_data.get('userId', 'N/A')}: {insert_error}")
                    print(f"Problematic data: {user_data}")

            print(f"Attempted to insert {inserted_count} users.")
            print("Committing insert transaction...")
            insert_transaction.commit()
            print(f"{inserted_count} users processed and successfully inserted.")

        except exc.SQLAlchemyError as e:
            print(f"An error occurred during data insertion: {e}")
            print("Rolling back insert transaction...")
            insert_transaction.rollback()
            print("Insert transaction rolled back.")
        except Exception as e:
            print(f"An unexpected error occurred during insertion: {e}")
            print("Rolling back insert transaction...")
            insert_transaction.rollback()
            print("Insert transaction rolled back.")

except exc.SQLAlchemyError as db_conn_error:
    print(f"Database connection/engine creation error: {db_conn_error}")
    print("Check .env settings and DB server status.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("--- Script Finished ---") # 종료 로그 추가 