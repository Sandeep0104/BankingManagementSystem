import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "sqlite:///./bank.db")

if _raw_url.startswith("sqlite"):
    engine = create_engine(
        _raw_url,
        connect_args={"check_same_thread": False}
    )
else:
    # Parse the URL and force the drivername to use psycopg (v3)
    # This is the most reliable method - avoids all string manipulation edge cases
    parsed = make_url(_raw_url)
    final_url = parsed.set(drivername="postgresql+psycopg")
    
    engine = create_engine(
        final_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
