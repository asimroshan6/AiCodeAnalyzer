import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from database import Base, get_db
from auth import get_current_user, bcrypt_context
from main import app
from models import User, CodeSubmission


TEST_DB_URL = "sqlite:///./testdb.db"

engine = create_engine(
    url=TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    def override_get_current_user():
        return {"user_id": 1, "username": "johndoe"}
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    user = User(username="johndoe", email="johndoe@gmail.com", hashed_password=bcrypt_context.hash("john123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_code_submission(db_session, test_user):
    submission = CodeSubmission(
        user_id=test_user.id,
        heading="Test Heading",
        code_text="Test Code",
        ai_result={"test": "ai result"},
    )
    
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission