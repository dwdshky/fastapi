from fastapi import APIRouter, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from .. import models, schemas, auth2
from ..database import get_db


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostRes])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(auth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # cur.execute("""SELECT * FROM posts""")
    # posts = cur.fetchall()
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.CreatePost, db: Session = Depends(get_db), current_user: int = Depends(auth2.get_current_user)
):
    # cur.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cur.fetchone()
    # conn.commit()

    # print(current_user.id)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostRes)
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(auth2.get_current_user)):
    # cur.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cur.fetchone()

    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"A post with id {id} was not found!")

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(auth2.get_current_user)):

    # cur.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # del_post = cur.fetchone()
    # conn.commit()

    query_post = db.query(models.Post).filter(models.Post.id == id)
    del_post = query_post.first()
    if del_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid ID: {id}")

    if del_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action!"
        )
    query_post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.CreatePost,
    db: Session = Depends(get_db),
    current_user: int = Depends(auth2.get_current_user),
):

    # cur.execute(
    #     """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #     (post.title, post.content, post.published, str(id)),
    # )
    # upd_post = cur.fetchone()
    # conn.commit()

    query_post = db.query(models.Post).filter(models.Post.id == id)
    upd_post = query_post.first()

    if upd_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid ID: {id}")

    if upd_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action!"
        )

    query_post.update(post.dict(), synchronize_session=False)
    db.commit()

    return upd_post
