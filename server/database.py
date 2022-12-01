import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

PATH_DB = "detection.db"

engine = create_engine(
    "sqlite:///" + PATH_DB,
    connect_args={"check_same_thread": False},
    encoding='utf-8',
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
