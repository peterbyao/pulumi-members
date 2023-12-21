from pydantic import BaseModel
from typing import Optional, List

class MemberSchema(BaseModel):
    member_name: str
    portfolio_value: float
    age: int


class Member(MemberSchema):
    id: Optional[int]

    class Config:
        orm_mode = True
