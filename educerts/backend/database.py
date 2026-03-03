from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use PostgreSQL from environment variable, fallback to SQLite for local dev
import os
db_path = os.path.join(os.path.dirname(__file__), "educerts.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

# psycopg2 driver for PostgreSQL
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
