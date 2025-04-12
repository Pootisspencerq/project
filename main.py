from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from auth import get_current_user, create_access_token, authenticate_user, get_password_hash, get_salt
from database import SessionLocal, engine, Base
from models import Author, Book, User
from schemas import BookCreate, UserCreate
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()  # Ensure this is only defined once
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    salt = get_salt()
    hashed = get_password_hash(user.password + salt)
    db_user = User(login=user.login, password=hashed + ':' + salt)
    db.add(db_user)
    db.commit()
    return {"msg": "User registered"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.login})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    author = db.query(Author).filter(Author.name == book.author).first()
    if not author:
        author = Author(name=book.author)
        db.add(author)
        db.commit()
        db.refresh(author)
    new_book = Book(title=book.title, pages=book.pages, author_id=author.id)
    db.add(new_book)
    db.commit()
    return {"message": "Book added successfully"}

@app.get("/books/{author}")
def get_books_by_author(author: str, db: Session = Depends(get_db)):
    author_obj = db.query(Author).filter(Author.name == author).first()
    if not author_obj:
        raise HTTPException(status_code=404, detail="Author not found")
    return [{"title": book.title, "pages": book.pages} for book in author_obj.books]

@app.put("/books/")
def update_book(book: BookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    author = db.query(Author).filter(Author.name == book.author).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    book_obj = db.query(Book).filter(Book.title == book.title, Book.author_id == author.id).first()
    if not book_obj:
        raise HTTPException(status_code=404, detail="Book not found")
    book_obj.pages = book.pages
    db.commit()
    return {"message": "Book updated successfully"}

@app.delete("/books/")
def delete_book(author: str, title: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    author_obj = db.query(Author).filter(Author.name == author).first()
    if not author_obj:
        raise HTTPException(status_code=404, detail="Author not found")
    book_obj = db.query(Book).filter(Book.title == title, Book.author_id == author_obj.id).first()
    if not book_obj:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book_obj)
    db.commit()
    return {"message": "Book deleted successfully"}
