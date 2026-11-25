from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from models import User
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt


router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "2107a98339969148cba5bd15291dd5377d6c1f3f0eda87c78840a8024276123f"
ALGORITHM = "HS256"
class CreateUser(BaseModel):
    username : str
    email : str
    firstname : str
    lastname : str
    password : str
    role : str
    phn : str
    
class updateUser(BaseModel):
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    firstname: Optional[str] = Field(default=None)
    lastname: Optional[str] = Field(default=None)
    phn: Optional[str] = Field(default=None)
    
class updatePassword(BaseModel):
    current_password: str
    new_password: str

def authenticate_user(username, password, db):
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        return False
    
    if bcrypt_context.verify(password, user.hash_password):
        return user
    
    return False

def create_access_token(username: str, user_id: int, role: str, expires_date: timedelta):
    encode ={"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_date
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")
        if username is None or user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {'username': username, 'user_id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/createUser')
def create_user(db : db_dependency, new_user: CreateUser):
    model_user = User(
        username=new_user.username,
        email=new_user.email,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        hash_password=bcrypt_context.hash(new_user.password),
        is_active=True,
        role=new_user.role,
        phn=new_user.phn
    )
    db.add(model_user)
    db.commit()
    
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.post('/login')
def login_user(db : db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    authenticated = authenticate_user(form_data.username, form_data.password, db)
    if not authenticated :
        return JSONResponse(status_code=401, content={"message": "Invalid username or password"})
    
    token = create_access_token(authenticated.username, authenticated.id, authenticated.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


@router.put('/editUser')
def update_user(user: user_dependency, db: db_dependency, updated_user: updateUser):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_to_update = db.query(User).filter(User.id == user['user_id']).first()
    
    update_data = updated_user.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(user_to_update, key, value)
        
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "User updated successfully"})

@router.put('/updatePassword')
def update_password(user: user_dependency, db: db_dependency, updated_password: updatePassword):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_to_update = db.query(User).filter(User.id == user['user_id']).first()
    
    if not bcrypt_context.verify(updated_password.current_password, user_to_update.hash_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    user_to_update.hash_password = bcrypt_context.hash(updated_password.new_password)
    
    db.add(user_to_update)
    db.commit()
    
    return JSONResponse(status_code=200, content={"message": "Password updated successfully"})