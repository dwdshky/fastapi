from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[schemas.UserRes])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.User).all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRes)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    # Hash Password
    hashed_pass = utils.hash(user.password)
    user.password = hashed_pass

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserRes)
def get_post(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A user with id {id} was not found!")

    return user
