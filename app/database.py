from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

import datetime as dt
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Text, Float

from database import Base

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    mail = Column(String, unique=True, default="empty")
    phone = Column(String(length=10), unique=True, default="empty")

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, index=True)
    id_client = Column(Integer, ForeignKey("client.id"))
    date_created = Column(Date, default=dt.datetime.utcnow)
    date_last_updated = Column(Date, default=dt.datetime.utcnow)
    text = Column(Text)
    sentiment = Column(String, default="empty")
    positive = Column(Float(), default="0") 
    neutral = Column(Float(), default="0") 
    negative = Column(Float(), default="0") 
    
Base.metadata.create_all(engine, checkfirst=True)