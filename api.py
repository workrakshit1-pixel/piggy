# src/piggy/api.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import Db, crud, schemas, assistant
from typing import List

router = APIRouter(prefix="/api")

@router.post("/expenses", response_model=schemas.ExpenseOut)
def create_expense(payload: schemas.ExpenseCreate, db_s: Session = Depends(Db.get_db)):
    manager = crud.ExpenseManager(db_s)
    exp = manager.add_expense(payload)
    return exp

@router.get("/expenses", response_model=List[schemas.ExpenseOut])
def list_expenses(limit: int = 100, offset: int = 0, db_s: Session = Depends(Db.get_db)):
    manager = crud.ExpenseManager(db_s)
    return manager.get_expenses(limit=limit, offset=offset)

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db_s: Session = Depends(Db.get_db)):
    manager = crud.ExpenseManager(db_s)
    ok = manager.delete_expense(expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"success": True, "id": expense_id}

@router.get("/total")
def get_total(db_s: Session = Depends(Db.get_db)):
    manager = crud.ExpenseManager(db_s)
    return {"total": manager.total()}

@router.post("/assistant", response_model=schemas.AssistResponse)
def assistant_endpoint(req: schemas.AssistRequest, db_s: Session = Depends(Db.get_db)):
    manager = crud.ExpenseManager(db_s)
    reply, success, data = assistant.parse_and_handle(req.message, manager)
    # Convert data to schema if present
    data_out = None
    if data:
        data_out = [schemas.ExpenseOut.from_orm(x) for x in data]
    return {"reply": reply, "success": success, "data": data_out}
