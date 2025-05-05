# src/models.py
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Text, Date, BigInteger, ForeignKey, FLOAT
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from .database import Base
# import enum #<-- UserTypeEnum 정의는 여기서 안 함 (DB는 VARCHAR 가정)

# DB 테이블 구조와 1:1 매핑되는 SQLAlchemy 모델들
class User(Base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    login_id = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    birthday = Column(Date, nullable=False)
    major = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=False)
    usertype = Column(String(50), nullable=False) # DB는 VARCHAR(50) 사용
    is_email_verified = Column(TINYINT, default=0)
    interest = Column(Text) # 매칭 점수 계산 위해 포함
    isOn = Column(TINYINT, default=1)
    visibility_score = Column(FLOAT, default=1.0)

    # Relationships
    korean_attribute = relationship("KoreanTutorAttribute", back_populates="user", uselist=False, cascade="all, delete-orphan")
    foreign_attribute = relationship("ForeignTuteeAttribute", back_populates="user", uselist=False, cascade="all, delete-orphan")

class KoreanTutorAttribute(Base):
    __tablename__ = "korean_tutor_attribute"

    korean_tutor_attribute_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    reputation = Column(BigInteger)
    fix_count = Column(BigInteger)

    user = relationship("User", back_populates="korean_attribute")

class ForeignTuteeAttribute(Base):
    __tablename__ = "foreign_tutee_attribute"

    foreign_tutee_attribute_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    country = Column(String(255))

    user = relationship("User", back_populates="foreign_attribute")
