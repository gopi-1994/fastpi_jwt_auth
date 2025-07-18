from fastapi import FastAPI, HTTPException, status, Depends
import auth
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from auth import get_current_user

app = FastAPI()

app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]

@app.get('/', status_code=status.HTTP_200_OK)
async def user(user: user_dependancy, db: db_dependancy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")
    return {"message": f"Hello, {user}!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)