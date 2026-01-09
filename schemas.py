from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserModel(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    
class CodeSubmissionModel(BaseModel):
    code_text: str = Field(...)
    
class CodeHistoryOut(BaseModel):
    id: int
    user_id: int
    code_text: str
    ai_result: Optional[dict]
    created_at: datetime
    
    class ConfigDict:
        from_attributes = True
        