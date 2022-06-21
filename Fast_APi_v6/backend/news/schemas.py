from typing import Optional
from pydantic import BaseModel


class News(BaseModel):
    time: int
    media: str
    topic: str
    title: str
    news : str
    abs_news : str

    class Config:
        orm_mode = True


class NewsUpdate(BaseModel):
    topic: str

    class Config:
        orm_mode = True

