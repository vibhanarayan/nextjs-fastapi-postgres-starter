from sqlalchemy import select
from sqlalchemy.orm import Session
from db_engine import sync_engine
from models import User


def seed_users_if_needed():
    with Session(sync_engine) as session:
        with session.begin():
            # Check for the existence of the initial user by filtering with a unique identifier
            existing_user = session.execute(select(User).filter_by(name="Alice")).scalar_one_or_none()
            if existing_user is not None:
                print("User 'Alice' already exists, skipping seeding")
            else:
                print("Seeding user 'Alice'")
                session.add(User(name="Alice"))

            # Check for the existence of the bot user by filtering with id=0
            bot_user = session.query(User).filter_by(id=0).first()
            if bot_user is not None:
                print("Bot user already exists, skipping seeding")
            else:
                print("Seeding bot user")
                session.add(User(id=0, name="Bot"))

            session.commit()
