from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel
from .database import  Base
from .database import ENGINE
from datetime import  datetime

class News(Base):
    tb =  str(datetime.today().strftime('%Y{}%m{}%d{}').format(*'년월일'))
    __tablename__ = tb
    time = Column(DateTime, primary_key=True)
    media = Column(String())
    topic = Column(String())
    title = Column(String())
    news = Column(String())
    abs_news = Column(String())
    url = Column(String())

class Topic(BaseModel):
    time: int
    media: str
    topic: str
    title: str
    news: str
    abs_news: str
    url : str


