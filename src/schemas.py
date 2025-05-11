from pydantic import BaseModel, Field
from typing import List, Optional
import enum

# UserType Pydantic Enum (API 용)
class UserTypeEnumPydantic(str, enum.Enum):
    NATIVE = "NATIVE"  # KOREAN 대신 NATIVE 사용
    FOREIGN = "FOREIGN"

# API 응답 및 내부 로직에서 사용할 통합 User 모델
class UserSchema(BaseModel):
    userId: int = Field(..., alias='user_id')
    username: str = Field(..., alias='name')
    userType: UserTypeEnumPydantic = Field(..., alias='usertype')
    major: Optional[str] = None
    country: Optional[str] = None
    interest: List[str] = []
    reputation: Optional[int] = 0
    isOn: bool = Field(..., alias='is_on')
    # visibility_score: Optional[float] = Field(1.0, alias='visibility_score')

    class Config:
        orm_mode = True # SQLAlchemy 모델 -> Pydantic 변환 허용 (v1 style)
        from_attributes = True # SQLAlchemy 모델 -> Pydantic 변환 허용 (v2 style)
        allow_population_by_field_name = True # alias 허용 (v1 style)
        populate_by_name = True # alias 허용 (v2 style)

# 필요시 다른 스키마 추가 (예: UserMatching)
# class UserMatching(BaseModel):
#     matchId: int
#     nativeUserId: int
#     foreignUserId: int
#     status: str
#     created_at: str # 또는 datetime
#     updated_at: str # 또는 datetime 

# API 요청 본문용 스키마 (예시)
class MatchingRequestSchema(BaseModel):
    userId: int
    userType: UserTypeEnumPydantic

# UserBase(BaseModel):
#     user_id: int
#     name: str
#     usertype: UserTypeEnumPydantic
#     major: Optional[str] = None
#     country: Optional[str] = None
#     interest: List[str] = []
#     reputation: Optional[int] = 0
#     isOn: bool = False
#     visibility_score: Optional[float] = 1.0
#
#     class Config:
#         orm_mode = True
#         from_attributes = True
#         allow_population_by_field_name = True
#         populate_by_name = True 