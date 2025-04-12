from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    login: str
    password: str

class BookCreate(BaseModel):
    title: str
    author: str = Field(min_length=3, max_length=30)
    pages: int = Field(ge=10)
