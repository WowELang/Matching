import random

# 데이터 생성을 위한 샘플 값들
majors = ['컴공', '경영', '수학', '물리', '화학', '생물', '영문', '철학', '심리', '경제']
countries = ['중국', '미국', '일본', '프랑스', '독일', '베트남', '인도', '러시아', '브라질', '캐나다']
interests = ['프로그래밍', '음악', '여행', '영화', '독서', '운동', '요리', '사진', '게임', '미술']

def generate_mock_users(num_korean=25, num_foreign=25):
    """지정된 수만큼 한국인/외국인 목업 유저 데이터를 생성하여 리스트로 반환"""
    mock_users_raw = []
    total_users = num_korean + num_foreign
    user_id_counter = 1

    # 한국인 생성
    for _ in range(num_korean):
        user_id = user_id_counter
        is_on_status = random.choice([True, False]) # isOn 랜덤 (True/False)
        # is_on_status = user_id % 2 != 0 # 또는 ID 기반으로 결정
        reputation_val = random.randint(60, 100)
        fix_count_val = random.randint(0, 3)
        user_data = {
            "userId": user_id,
            "username": f'한국인{user_id}',
            "userType": 'KOREAN',
            "major": random.choice(majors),
            "country": '한국',
            "interest": random.sample(interests, 3),
            "reputation": reputation_val,
            "fix_count": fix_count_val, # DB의 fix_count에 해당
            "isOn": is_on_status,
            # DB 스키마에 필요한 추가 필드 (populate 스크립트에서 사용)
            "login_id": f"user{user_id}",
            "email": f"user{user_id}@example.com",
            "password": "password123",
            "birthday": f"{1995 + random.randint(0, 8)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "gender": random.choice(["MALE", "FEMALE"])
        }
        mock_users_raw.append(user_data)
        user_id_counter += 1

    # 외국인 생성
    for i in range(num_foreign):
        user_id = user_id_counter
        is_on_status = random.choice([True, False]) # isOn 랜덤
        # is_on_status = user_id % 2 != 0
        country_val = random.choice(countries)
        user_data = {
            "userId": user_id,
            "username": f'유학생{i+1}',
            "userType": 'FOREIGN',
            "major": random.choice(majors),
            "country": country_val,
            "interest": random.sample(interests, 3),
            "reputation": None, # 외국인은 reputation 없음 (DB 스키마 기준)
            "fix_count": None, # 외국인은 fix_count 없음 (DB 스키마 기준)
            "isOn": is_on_status,
            # DB 스키마에 필요한 추가 필드
            "login_id": f"user{user_id}",
            "email": f"user{user_id}@example.com",
            "password": "password123",
            "birthday": f"{1995 + random.randint(0, 8)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "gender": random.choice(["MALE", "FEMALE"])
        }
        mock_users_raw.append(user_data)
        user_id_counter += 1

    return mock_users_raw

if __name__ == '__main__':
    # 스크립트 직접 실행 시 생성된 데이터 샘플 출력 (테스트용)
    generated_users = generate_mock_users(5, 5)
    import json
    print(json.dumps(generated_users, indent=2, ensure_ascii=False)) 