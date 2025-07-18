from datetime import datetime, timedelta, timezone
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

dcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_brearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):    
    access_token: str
    token_type: str
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
db_dependancy = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED )
async def create_user(db: db_dependancy, user: CreateUserRequest):
    create_user_model = User(
        username=user.username,
        password=dcrypt_context.hash(user.password))
    db.add(create_user_model)
    db.commit()
    
    
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    
    return {"access_token": token, "token_type": "bearer"}

def authenticate_user(username:str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not dcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username:str, user_id : int, expires_delta: timedelta | None = None):
    to_encode = {"sub": username, "id": user_id}
    if expires_delta:
   
        expire = datetime.now(timezone.utc) + expires_delta
    else:    
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
    
def get_current_user(token: Annotated[str, Depends(oauth2_brearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Could not validate credentials"
            
        )
    