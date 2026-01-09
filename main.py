from fastapi import FastAPI, Depends, status, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import List, Optional
from sqlalchemy import or_, and_
from database import get_db, Session, engine
from models import User, CodeSubmission, Base
from schemas import UserModel, CodeSubmissionModel, CodeHistoryOut
from auth import hash_password, create_access_token, verify_user, get_current_user
from ai import explain_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


##  templates  ##

@app.get("/", name="")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register/", name="register")
def user_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login/", name="login")
def user_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/submit-code/", name="submit-code")
def code_submit(request: Request):
    return templates.TemplateResponse("code-submit.html", {"request": request})

@app.get("/history/", name="history")
def history(request: Request):
    return templates.TemplateResponse("code-history.html", {"request": request})

@app.get("/history/{id}/", name="single-chat")
def get_chat_by_id(request: Request, id: int):
    return templates.TemplateResponse("single-chat.html", {"request": request, "id": id})


### End Points ###


@app.post("/user/register/")
def user_register(new_user: UserModel, db: Session = Depends(get_db)):
    
    user_exist = db.query(User).filter(or_(User.username == new_user.username, User.email == new_user.email)).first()
    
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user already exist"
        )
    
    user = User(username=new_user.username, email=new_user.email, hashed_password = hash_password(new_user.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "user created", "user_id": user.id, "username": user.username, "email": user.email}


@app.post("/user/login/")
def user_login(user_details: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = verify_user(user_details.username, user_details.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password"
        )
        
    access_token = create_access_token(user.username, user.id, timedelta(minutes=20))
        
    return {"message": "user authenticated", "user_id": user.id, "username": user.username, "access_token": access_token}


@app.post("/submit-code/")
def submit_code(code_text: CodeSubmissionModel, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    response = explain_code(code_text.code_text)
    code_model = CodeSubmission(user_id=user.get("user_id"), code_text=code_text.code_text, heading=response.get("heading"), ai_result=response)
    db.add(code_model)
    db.commit()
    db.refresh(code_model)
    return {"code_text": code_model.code_text, "ai_response": code_model.ai_result}


@app.get("/api/history/", response_model=List[CodeHistoryOut])
def history(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    user_id = user.get("user_id")
    code_history = db.query(CodeSubmission).filter(CodeSubmission.user_id == user_id).order_by(CodeSubmission.created_at.desc()).all()
    return code_history


@app.get("/api/history/{id}/", response_model=Optional[CodeHistoryOut])
def get_chat_by_id(id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chat = db.query(CodeSubmission).filter(and_(CodeSubmission.id == id, CodeSubmission.user_id == user.get("user_id"))).first()
    return chat


@app.get("/search/", response_model=Optional[List[CodeHistoryOut]])
def search_in_history(q: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    query = f"%{q}%"
    searched_codes = db.query(CodeSubmission).filter(
                    CodeSubmission.user_id == user.get("user_id")
                    ).filter(or_(
                        CodeSubmission.code_text.ilike(query), 
                        CodeSubmission.heading.ilike(query)
                     )).all()
                    
    return searched_codes


@app.delete("/history/{id}/")
def delete_chat_by_id(id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    chat = db.query(CodeSubmission).filter(and_(CodeSubmission.id == id, CodeSubmission.user_id == user.get("user_id"))).first()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "chat deleted successfully"}
