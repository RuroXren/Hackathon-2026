#--- ИМПОРТ ---
import os
from fastapi import FastAPI, Form, Depends
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

@site.get("/")
def home():
    return {"status": "Бэкэнд работает"}

@site.post('/register')
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_user = User(username=username, password=password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {'message': f'{username} добавлен'}

@site.post('/login')
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if not user or user.password != password:
        return {'error': "Неверный пароль или логин"}
    
    return {'message': f"Приветсвую, {username}"}
