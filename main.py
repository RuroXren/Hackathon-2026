#--- ИМПОРТ ---
import os
from fastapi import FastAPI, Form, Depends

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

    return RedirectResponse(url="/test", status_code=303)

@site.post('/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != password:
        return {'error': "Неверный пароль или логин"}
    
    return RedirectResponse(url="/test", status_code=303)
