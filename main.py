from fastapi import FastAPI, HTTPException, status, Depends
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]

@app.get('/')
async def user(user: None, db: db_dependancy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return {"message": f"Hello, {user}!"}
