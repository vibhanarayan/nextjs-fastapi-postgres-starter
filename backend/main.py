from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session
from db_engine import sync_engine, engine
from seed import seed_users_if_needed
from sqlalchemy.ext.asyncio import AsyncSession
from schema import UserCreate, MessageCreate, Message
from models import User
from crud import create_user, get_messages, create_message

seed_users_if_needed()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Synchronous session for CRUD operations
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Asynchronous session for other operations
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserRead(BaseModel):
    id: int
    name: str


@app.get("/users/me")
async def get_my_user():
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Sample logic to simplify getting the current user. There's only one user.
            result = await session.execute(select(User))
            user = result.scalars().first()

            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserRead(id=user.id, name=user.name)


@app.post("/users/", response_model=UserRead)
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    db_user = create_user(next(get_sync_db()), user)
    return UserRead(id=db_user.id, name=db_user.name)


@app.get("/messages/", response_model=list[Message])
async def read_messages(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)):
    messages = get_messages(next(get_sync_db()), skip=skip, limit=limit)
    return messages


@app.post("/messages/", response_model=Message)
async def create_message_endpoint(message: MessageCreate, db: AsyncSession = Depends(get_async_db)):
    db_message = create_message(next(get_sync_db()), message)
    return db_message


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: int = Query(...), db: Session = Depends(get_sync_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Save user message
            user_message = MessageCreate(content=data, user_id=user_id)  # Assuming user_id 1 for simplicity
            create_message(db, user_message)
            # Respond to user
            response = f"Bot response to: {data}"
            bot_message = MessageCreate(content=response, user_id=0)  # Assuming user_id 0 for bot
            create_message(db, bot_message)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
