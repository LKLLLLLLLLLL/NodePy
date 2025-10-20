from sqlalchemy import String, Integer, Column, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
import os


"""
Session management.
"""
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL)

def get_session() -> Session:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

"""
The models used in database.
"""
Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    file_occupy = Column(Integer, default=0, nullable=False)  # in Byte
    file_total_space = Column(Integer, default=5 * 1024 * 1024 * 1024, nullable=False)  # 5 GB default

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_key = Column(String, nullable=False) # MinIO object key
    format = Column(Enum("jpg", "png", "csv", "pdf", name="file_format"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_size = Column(Integer, nullable=False) # Byte
    upload_time = Column(String, nullable=False)  # ISO format datetime string
