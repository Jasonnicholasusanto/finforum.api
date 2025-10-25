from fastapi import HTTPException, status
from sqlmodel import Session
from app.schemas.favourite_stock import FavouriteStockCreate, FavouriteStockUpdate
from app.crud.favourite_stock import favourite_stock as crud_favourite_stock


def get_favourite_stock_by_symbol(session: Session, user_id: str, symbol: str):
    return crud_favourite_stock.get_by_symbol(session, user_id=user_id, symbol=symbol)


def list_favourite_stocks(session: Session, user_id: str):
    return crud_favourite_stock.get_all_by_user(session, user_id=user_id)


def add_favourite_stock(session: Session, user_id: str, payload: FavouriteStockCreate):
    existing = crud_favourite_stock.get_by_symbol(session, user_id=user_id, symbol=payload.symbol)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock already in favourites list."
        )

    new_item = crud_favourite_stock.create(
        session=session,
        obj_in=payload,
        user_id=user_id,
    )
    return new_item


def remove_favourite_stock(session: Session, id: int,):
    stock = crud_favourite_stock.get_by_id(session, id=id)
    if not stock:
        raise HTTPException(status_code=404, detail="Favourite stock not found.")
    
    deleted_stock = crud_favourite_stock.remove(session, id=stock.id)
    return deleted_stock


def update_favourite_stock(session: Session, user_id: str, id: int, data: FavouriteStockUpdate):
    stock = crud_favourite_stock.get_by_id(session, user_id=user_id, id=id)
    if not stock:
        raise HTTPException(status_code=404, detail="Favourite stock not found.")

    updated = crud_favourite_stock.update(session=session, db_obj=stock, obj_in=data)
    return updated
