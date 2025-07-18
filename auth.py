from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "0553abd6dc9e05eae3f5f0ae457d47ccbf9a10b90bfc9cba896c643cdf912c2cdf702314aa41a33a0cdcf294547eda3a"
ALGORITHM = "HS256"

dcrypt_context = CryptContext(schemas=["bcrypt"], deprecated="auto")
oauth2_brearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    password: str
    
class Tokern(BaseModel):    
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()