#--- ИМПОРТ ---
import os
from fastapi import FastAPI, Form, Depends, HTTPException

from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

#--- Поключаем движок к базе данных ---

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#--- Создание таблицы ---

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

#--- Логика сайта ---

site = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

site.mount("/static", StaticFiles(directory="static"), name="static")

#--- Страницы сайта (GET) ---

@site.get("/")
def home():
    return FileResponse("static/index.html")

@site.get("/test")
def test():
    return FileResponse("static/test.html")

#--- Команды от сайта (POST) ---

@site.post('/register')
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_user = User(username=username, password=password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "username": new_user.username,
        "redirect_url": "/static/test.html"
    }

@site.post('/login')
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid")
    
    return {
        "status": "success",
        "username": user.username,
        "redirect_url": "/static/test.html"
    }