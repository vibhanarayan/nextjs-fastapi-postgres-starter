from pydantic import BaseModel
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    user_id: int


class Message(MessageBase):
    id: int
    timestamp: datetime
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    messages: list[Message] = []

    class Config:
        orm_mode = True
