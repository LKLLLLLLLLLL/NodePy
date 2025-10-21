from sqlalchemy import String, Integer, Column, ForeignKey, Enum, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text
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
    file_total_space = Column(BigInteger, default=5 * 1024 * 1024 * 1024, nullable=False)  # 5 GB default

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String, nullable=False)  # Original file name
    file_key = Column(String, nullable=False) # MinIO object key
    format = Column(Enum("jpg", "png", "csv", "pdf", name="file_format"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_size = Column(BigInteger, nullable=False) # Byte
    upload_time = Column(String, nullable=False)  # ISO format datetime string

# Create database tables
Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    conn.execute(
        text("""
        CREATE OR REPLACE FUNCTION check_user_storage_limit() RETURNS trigger AS $$
        DECLARE
            total_occupy BIGINT;
            user_limit BIGINT;
        BEGIN
            SELECT COALESCE(SUM(file_size), 0) INTO total_occupy
            FROM files
            WHERE user_id = NEW.user_id;
            SELECT file_total_space INTO user_limit
            FROM users
            WHERE id = NEW.user_id;
            IF total_occupy > user_limit THEN
                RAISE EXCEPTION 'User storage limit exceeded';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    )
    conn.execute(
        text("""
        CREATE TRIGGER files_check_storage_limit_before
        BEFORE INSERT OR UPDATE ON files
        FOR EACH ROW EXECUTE FUNCTION check_user_storage_limit();
    """)
    )
    conn.commit()
