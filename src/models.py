# src/models.py
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Text, Date, BigInteger, ForeignKey, FLOAT, Boolean, Float
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from .database import Base
import enum

# DB 저장을 위한 UserType Enum (SQLAlchemy용)
class UserTypeEnumDB(enum.Enum):
    NATIVE = "NATIVE"
    FOREIGN = "FOREIGN"

# DB 테이블 구조와 1:1 매핑되는 SQLAlchemy 모델들
class User(Base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True, index=True)
    login_id = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    birthday = Column(String(255)) # DB 스키마 이미지에는 date 타입, 모델은 String. 일치 필요시 String(255) 또는 Date로 통일
    major = Column(String(255))
    gender = Column(String(50))
    usertype = Column(SQLEnum(UserTypeEnumDB), nullable=False)
    is_email_verified = Column(Boolean, default=False) # DB 스키마 이미지에는 tinyint(1)
    is_on = Column(Boolean, default=False, name="is_on") # 속성명 is_on, DB 컬럼명 is_on으로 가정. 이전 isOn에서 변경
    # visibility_score 컬럼은 DB에 없으므로 모델에서도 제거
    # visibility_score = Column(Float, default=1.0)

    # User와 KoreanTutorAttribute 간의 일대일 관계 (이름 변경)
    korean_attribute = relationship("KoreanTutorAttribute", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # User와 ForeignTuteeAttribute 간의 일대일 관계 (이름 변경)
    foreign_attribute = relationship("ForeignTuteeAttribute", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # User와 Interest 간의 일대다 관계
    interests = relationship("Interest", back_populates="user", cascade="all, delete-orphan")

# KoreanUserAttribute -> KoreanTutorAttribute로 클래스명 및 테이블명 변경
class KoreanTutorAttribute(Base):
    __tablename__ = "korean_tutor_attribute" # 테이블명 변경
    user_id = Column(BigInteger, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    reputation = Column(Integer, default=0)
    # 모델 속성명은 fix_cnt, 실제 DB 컬럼명은 fix_count에 매핑
    fix_cnt = Column("fix_count", Integer, default=0)
    user = relationship("User", back_populates="korean_attribute")

# ForeignUserAttribute -> ForeignTuteeAttribute로 클래스명 및 테이블명 변경
class ForeignTuteeAttribute(Base):
    __tablename__ = "foreign_tutee_attribute" # 테이블명 변경
    user_id = Column(BigInteger, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    country = Column(String(255))
    # User와의 관계 설정 (수정)
    user = relationship("User", back_populates="foreign_attribute")

# 새로운 Interest 모델 정의
class Interest(Base):
    __tablename__ = "interest"

    interest_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    interest_name = Column(String(100), nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True) # user_id 외래키, 인덱스 추가

    # Interest와 User 간의 다대일 관계 (새로 추가)
    user = relationship("User", back_populates="interests")
