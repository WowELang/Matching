    # test_env.py
import os
from dotenv import load_dotenv

    # .env 파일의 경로를 명시적으로 지정해볼 수도 있습니다.
    # 아래는 현재 파일(test_env.py)이 있는 디렉토리의 .env 파일을 찾는 예시입니다.
    # 만약 .env 파일이 다른 곳에 있다면 경로를 맞게 수정해야 합니다.
    # dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    # load_dotenv(dotenv_path=dotenv_path)
    
    # 기본적으로 현재 작업 디렉토리에서 .env를 찾습니다.
load_dotenv() 

db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {db_url}")

if db_url:
    print("환경 변수를 성공적으로 읽었습니다.")
    # URL 파싱 시뮬레이션 (간단하게)
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        print(f"  Scheme: {parsed.scheme}")
        print(f"  Netloc: {parsed.netloc}")
        print(f"  Path: {parsed.path}")
        print(f"  Port: {parsed.port}") # 이 부분이 int로 변환 가능한지 중요
        if parsed.port is None:
            print("  경고: URL에서 포트번호를 파싱하지 못했습니다.")
        else:
            print(f"  포트번호 (int로 변환 시도): {int(parsed.port)}")

    except Exception as e:
        print(f"URL 파싱 중 오류: {e}")
else:
    print("환경 변수를 읽어오지 못했습니다. .env 파일의 이름, 위치, 내용을 확인하세요.")
    