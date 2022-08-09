from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base


SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


# Dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Welcome to my api!!"}


def test_create_user():
    res = client.post("/users/", json={"email": "dwd@dwd.com", "password": "lamaya"})

    new_user = schemas.UserRes(**res.json())
    assert new_user.email == "dwd@dwd.com"
    assert res.status_code == 201
