import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.aws import rds

#URL_DATABASE = 'mysql+pymysql://root:TradingApp1234@localhost:3306/TradingApplication'
URL_DATABASE = "mysql+pymysql://" + rds.user + ":" + rds.password + "@" + rds.endpoint + ":3306/" + rds.schema
engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()
