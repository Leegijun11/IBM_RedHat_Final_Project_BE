from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.item_service import get_items, create_item
from pydantic import BaseModel

router = APIRouter(prefix="/api")

class ItemCreate(BaseModel):
    name: str
    description: str | None = None

@router.get("/items")
def read_items(db: Session = Depends(get_db)):
    return get_items(db)

@router.post("/items")
def add_item(item: ItemCreate, db: Session = Depends(get_db)):
    return create_item(db, item.name, item.description)