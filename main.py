from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Book(BaseModel):
    # id: UUID 
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    rating: float = Field(gt=0, lt=5)
    
BOOKS = []

@app.get('/')
async def get_books(db: Session = Depends(get_db)):
    return db.query(models.Books).all()

@app.post('/')
async def create_book(book: Book, db: Session = Depends(get_db)):
    # book.id = uuid4()
    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book

@app.put('/{book_id}')
async def update_book(book_id: int, book: Book, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()
    
    if book_model is None:
        raise HTTPException(status_code=status.HTTP_404, detail="Book not found")
    else:    
        book_model.title = book.title
        book_model.author = book.author
        book_model.description = book.description
        book_model.rating = book.rating
        
        db.commit()
        db.refresh(book_model)
        return book_model
    

@app.delete('/{book_id}')
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=status.HTTP_404, detail="Book not found")
    
    db.delete(book_model)
    db.commit()
    return {"message": f"{book_model.title} Book deleted successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)