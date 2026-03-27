#--- ИМПОРТ ---
import os
from fastapi import FastAPI, Form, Depends, HTTPException, Request

from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from passlib.context import CryptContext
import httpx

#--- ИНИЦАИЛИЗАЦИЯ ---

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#--- Создание таблицы ---

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hash_password = Column(String)

Base.metadata.create_all(bind=engine)

#--- Логика сайта ---

site = FastAPI()
site.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_h(password):
    return pwd_context.hash(password)

def verify_password(plain_pass, hash_pass):
    return pwd_context.verify(plain_pass, hash_pass)

#--- Страницы сайта (GET) ---

@site.get("/")
async def home():
    return FileResponse("static/index.html")

@site.get("/health")
async def health():
    return {"status": "healthy"}

#--- Команды от сайта (POST) ---

@site.post('/register')
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=username, hash_password=get_password_h(password))
    db.add(new_user)
    db.commit()

    return {
        "status": "success",
        "username": new_user.username,
        "redirect_url": "/static/test.html"
    }

@site.post('/login')
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hash_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "status": "success",
        "username": user.username,
        "redirect_url": "/static/test.html"
    }