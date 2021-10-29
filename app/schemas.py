import datetime as dt
from pydantic import BaseModel


class PostBase(BaseModel):
    text: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    id_client: int
    date_created: dt.date
    date_last_updated: dt.date

    class Config:
        orm_mode = True


class PostPrediction(Post):
    sentiment: str
    positive: float
    neutral: float
    negative: float


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    mail: str
    phone: str


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: int

    class Config:
        orm_mode = True