from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#DATABASE_URL = "postgresql://neondb_owner:npg_cYOH9bC7mKda@ep-falling-base-acq4r8c0-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"

DATABASE_URL = "postgresql://postgres:OuYYQdwFSBWFDihDyWELJaiUzfzvKfko@turntable.proxy.rlwy.net:26001/railway"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependência para abrir sessão com o banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()