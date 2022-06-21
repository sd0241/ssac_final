from fastapi import FastAPI
from typing import List
from starlette.middleware.cors import CORSMiddleware
from backend.news.database import SessionLocal
from backend.news.models import News, Topic

app = FastAPI()

@app.get("/news")
def read_NEWS():
    users = SessionLocal.query(News).all()

    return users

@app.get("/news/{topic}")
def read_NEWS(topic: str):
    news = SessionLocal.query(News).filter(News.topic == topic).all()
    return news

@app.post("/news")
def create_news(time: int, media: str, topic:str, title:str, news:str, abs_news:str):

    new = News()
    new.topic = topic
    new.time = time
    new.media = media
    new.title = title
    new.news = news
    new.abs_news = abs_news

    session.add(new)
    session.commit()

    return f"{topic} created..."

@app.put("/news")
def update_news(topics: List[Topic]):

    for i in topics:
        News = SessionLocal.query(News).filter(News.topic == i.topic).first()
        News.topic = i.topic
        News.time = i.time

    #users[0].name

    return f"{News[0].topic} updated..."

@app.delete("/News")
def delete_News(NEWS:str):
    New = SessionLocal.query(News).filter(News.topic == News).delete()
    SessionLocal.commit()

    return New