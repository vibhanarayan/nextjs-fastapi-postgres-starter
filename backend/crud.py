# backend/app/crud.py

from sqlalchemy.orm import Session
from models import User, Message
from schema import UserCreate, MessageCreate


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Message).offset(skip).limit(limit).all()


def create_message(db: Session, message: MessageCreate):
    db_message = Message(content=message.content, user_id=message.user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
