from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from database.session import get_session, engine

# IMPORT CATEGORY FIRST, THEN BOOK (8 lines total for this top section)
from models.category import Category
from models.book import Book, BookCreate, BookUpdate

# Automatically create database tables on startup
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Library API",
    description="A simple library management API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Library API"}

@app.post("/categories", response_model=Category)
def create_category(name: str, session: Session = Depends(get_session)):
    """Create a new category"""
    category = Category(name=name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@app.post("/books", response_model=Book)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    db_book = Book(**book.dict())
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@app.get("/books", response_model=List[Book])
def list_books(
    skip: int = 0,
    limit: int = 10,
    available: bool = None,
    session: Session = Depends(get_session)
):
    """List all books with optional filters"""
    query = select(Book)
    if available is not None:
        query = query.where(Book.available == available)
    return session.exec(query.offset(skip).limit(limit)).all()

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a specific book by ID"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
@app.get("/books/search", response_model=List[Book])
def search_books(
    author: Optional[str] = None,
    title: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Search for books by author or title"""
    query = select(Book)
    if author:
        query = query.where(Book.author.contains(author))
    if title:
        query = query.where(Book.title.contains(title))
    return session.exec(query).all()
# --- EXERCISE 3: UPDATE ENDPOINT ---
@app.patch("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)):
    """Update a book"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    update_data = book_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
        
    book.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(book)
    return book