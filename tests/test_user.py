from models import User
from auth import bcrypt_context


def test_register(client, db_session):
    body = {"username": "user", "email": "user@gmail.com", "password": "user123"}
    
    response = client.post(url="/user/register/", json=body)
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data is not None
    assert data["message"] == "user created"
    
    user = db_session.query(User).filter(User.username == body["username"]).first()
    
    assert user is not None
    assert user.username == body["username"]
    assert user.email == body["email"]
    assert bcrypt_context.verify(body["password"], user.hashed_password)


def test_exist_user_register(client, test_user):
    body = {"username": "johndoe", "email": "user@gmail.com", "password": "john123"}
    
    response = client.post("/user/register/", json=body)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "user already exist"
    
    
def test_login(client, test_user):
    body = {"username": "johndoe", "password": "john123"}
    
    response = client.post("/user/login/", data=body)
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["message"] == "user authenticated"
    assert data["user_id"] == test_user.id
    assert data["username"] == test_user.username
    
    
def test_wrong_login(client, test_user):
    body = {"username": "johndoe", "password": "wrongpassword"}
    
    response = client.post("/user/login/", data=body)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid username or password"