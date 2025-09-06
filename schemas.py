# src/piggy/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    category: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: str
    category: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class AssistRequest(BaseModel):
    message: str

class AssistResponse(BaseModel):
    reply: str
    success: bool
    data: Optional[List[ExpenseOut]] = None
