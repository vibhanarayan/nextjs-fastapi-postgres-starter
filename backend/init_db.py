# backend/app/init_db.py

from sqlalchemy.orm import sessionmaker
from db_engine import sync_engine
from models import Base, User, Message

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
session = SessionLocal()
bot_user = session.query(User).filter_by(id=0).first()
if not bot_user:
    bot_user = User(id=0, name="Bot")
    session.add(bot_user)
    session.commit()


def init_db():
    Base.metadata.create_all(bind=sync_engine)

if __name__ == "__main__":
    init_db()
