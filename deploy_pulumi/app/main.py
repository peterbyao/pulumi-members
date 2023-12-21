from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from src.schemas import MemberSchema, Member
from src.database import get_db, engine, SessionLocal
import src.models as models
from src.aws import rds
from typing import Annotated, List


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


db_dependency = Annotated[Session, Depends(get_db)]

# Index page
@app.get('/')
async def root():
    return {"message": "Hello World"}

# GET members
@app.get("/members/")
async def get_all_members(offset: int = 0,
                          limit: int = Query(default=10, le=100),
                          session: Session = Depends(get_db)):
    members = session.query(models.Member).offset(offset).limit(limit).all()
    return members

# POST add member_id
@app.post("/add_member/{member_name}/")
async def add_member(member_name: str, session: Session = Depends(get_db)):
    member = session.query(models.Member).filter(models.Member.member_name == member_name).first()
    if member:
        raise Exception("Member already exists")

    new_member = models.Member(member_name=member_name, portfolio_value=1000000, age=23)
    session.add(new_member)
    session.commit()
    session.refresh(new_member)

    return new_member